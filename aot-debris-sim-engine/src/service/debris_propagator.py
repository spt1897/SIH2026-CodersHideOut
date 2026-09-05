import heapq
import math
import h3


G = 9.81


async def get_cell_state(redis_client, cell):
    data = await redis_client.hgetall(
        f"cell_sim_nodes:{cell}"
    )

    if not data:
        return None

    return {
        "h3_index": cell,
        "elevation": float(data["elevation"]),
        "friction_coefficient": float(
            data["friction_coefficient"]
        ),
        "debris_state": data["debris_state"],
        "normalized_mass": float(
            data["normalized_mass"]
        ),
        "velocity": float(data["velocity"]),
        "specific_pe": float(
            data["specific_pe"]
        ),
        "specific_ke": float(
            data["specific_ke"]
        ),
        "arrival_time": float(
            data["arrival_time"]
        )
    }


async def save_cell_state(redis_client, cell, state):
    await redis_client.hset(
        f"cell_sim_nodes:{cell}",
        mapping={
            "debris_state": state["debris_state"],
            "normalized_mass": state["normalized_mass"],
            "velocity": state["velocity"],
            "specific_pe": state["specific_pe"],
            "specific_ke": state["specific_ke"],
            "arrival_time": state["arrival_time"]
        }
    )


def get_center_distance(cell1, cell2):

    return h3.great_circle_distance(
        h3.cell_to_latlng(cell1),
        h3.cell_to_latlng(cell2),
        unit="m"
    )


async def set_source_cell_state(
    redis_client,
    cell,
    detection_time
):

    state = await get_cell_state(
        redis_client,
        cell
    )

    if state is None:
        return None

    incoming_mass = 1.0
    incoming_velocity = 0.0

    # --------------------------------------------------------
    # STABLE
    # --------------------------------------------------------

    if state["debris_state"] == "STABLE":

        state["normalized_mass"] = incoming_mass
        state["velocity"] = incoming_velocity

    # --------------------------------------------------------
    # ACCUMULATED
    # --------------------------------------------------------

    elif state["debris_state"] == "ACCUMULATED":

        state["normalized_mass"] += incoming_mass
        state["velocity"] = incoming_velocity

    # --------------------------------------------------------
    # FLOWING
    # --------------------------------------------------------

    elif state["debris_state"] == "FLOWING":

        old_mass = state["normalized_mass"]
        old_velocity = state["velocity"]

        new_mass = old_mass + incoming_mass

        if new_mass > 0:
            new_velocity = (
                old_mass * old_velocity
                +
                incoming_mass * incoming_velocity
            ) / new_mass
        else:
            new_velocity = 0.0

        state["normalized_mass"] = new_mass
        state["velocity"] = new_velocity

    state["debris_state"] = "FLOWING"

    state["specific_pe"] = (
        state["elevation"] * G
    )

    state["specific_ke"] = (
        0.5 * state["velocity"] ** 2
    )

    if state["arrival_time"] == -1:
        state["arrival_time"] = float(
            detection_time
        )
    else:
        state["arrival_time"] = min(
            state["arrival_time"],
            float(detection_time)
        )

    await save_cell_state(
        redis_client,
        cell,
        state
    )

    return state


async def propagate_debris(    
    source_cell,
    detection_time,
    app
):
    redis_client  = app.state.redis_client
    """
    Propagate debris from source_cell.

    Returns:
        list[str]

    The returned list contains H3 cells in the order
    in which the debris reaches/traverses them.
    """

    # ========================================================
    # SOURCE
    # ========================================================

    source_state = await set_source_cell_state(
        redis_client,
        source_cell,
        detection_time
    )

    if source_state is None:
        return []

    # ========================================================
    # PRIORITY QUEUE
    #
    # (arrival_time, cell)
    # ========================================================

    queue = []

    heapq.heappush(
        queue,
        (
            source_state["arrival_time"],
            source_cell
        )
    )

    # Earliest arrival known for every cell
    earliest_arrival = {
        source_cell:
        source_state["arrival_time"]
    }

    # Cells already traversed
    traversed = set()

    # Final ordered cell list
    cells = []

    # ========================================================
    # PROPAGATION
    # ========================================================

    while queue:

        current_arrival, current_cell = (
            heapq.heappop(queue)
        )

        # ----------------------------------------------------
        # Ignore outdated queue entry
        # ----------------------------------------------------

        if current_arrival != earliest_arrival.get(
            current_cell
        ):
            continue

        # ----------------------------------------------------
        # Already traversed
        # ----------------------------------------------------

        if current_cell in traversed:
            continue

        traversed.add(current_cell)

        # ----------------------------------------------------
        # Current cell state
        # ----------------------------------------------------

        current_state = await get_cell_state(
            redis_client,
            current_cell
        )

        if current_state is None:
            continue

        # ----------------------------------------------------
        # APPEND TO RESULT
        #
        # Because heap is ordered by arrival_time,
        # this list is chronological.
        # ----------------------------------------------------

        cells.append(current_cell)

        # ----------------------------------------------------
        # Find neighboring H3 cells
        # ----------------------------------------------------

        neighbors = h3.grid_disk(
            current_cell,
            1
        )

        neighbors.discard(
            current_cell
        )

        reachable_neighbors = []

        # ====================================================
        # CALCULATE EACH NEIGHBOR
        # ====================================================

        for neighbor_cell in neighbors:

            if neighbor_cell in traversed:
                continue

            neighbor_state = await get_cell_state(
                redis_client,
                neighbor_cell
            )

            if neighbor_state is None:
                continue

            # ------------------------------------------------
            # Distance between centroids
            # ------------------------------------------------

            distance = get_center_distance(
                current_cell,
                neighbor_cell
            )

            if distance <= 0:
                continue

            # ------------------------------------------------
            # Current kinetic energy
            # ------------------------------------------------

            current_ke = (
                current_state["specific_ke"]
            )

            # ------------------------------------------------
            # Potential energy change
            #
            # Positive -> downhill
            # Negative -> uphill
            # ------------------------------------------------

            delta_pe = G * (
                current_state["elevation"]
                -
                neighbor_state["elevation"]
            )

            # ------------------------------------------------
            # Friction loss
            # ------------------------------------------------

            friction_loss = (
                neighbor_state[
                    "friction_coefficient"
                ]
                * G
                * distance
            )

            # ------------------------------------------------
            # KE at neighbor
            # ------------------------------------------------

            neighbor_ke = (
                current_ke
                +
                delta_pe
                -
                friction_loss
            )

            # ------------------------------------------------
            # Cannot reach this cell
            # ------------------------------------------------

            if neighbor_ke <= 0:
                continue

            # ------------------------------------------------
            # Velocity at neighbor
            # ------------------------------------------------

            neighbor_velocity = math.sqrt(
                2.0 * neighbor_ke
            )

            # ------------------------------------------------
            # Average velocity
            # ------------------------------------------------

            average_velocity = (
                current_state["velocity"]
                +
                neighbor_velocity
            ) / 2.0

            if average_velocity <= 0:
                continue

            # ------------------------------------------------
            # Travel time
            # ------------------------------------------------

            travel_time = (
                distance /
                average_velocity
            )

            candidate_arrival = (
                current_arrival
                +
                travel_time
            )

            reachable_neighbors.append({
                "cell": neighbor_cell,
                "distance": distance,
                "specific_ke": neighbor_ke,
                "velocity": neighbor_velocity,
                "travel_time": travel_time,
                "arrival_time": candidate_arrival
            })

        # ====================================================
        # MASS DISTRIBUTION
        #
        # M_i = M_current * v_i² / Σv_j²
        # ====================================================

        if reachable_neighbors:

            total_v_squared = sum(
                n["velocity"] ** 2
                for n in reachable_neighbors
            )

            for neighbor in reachable_neighbors:

                velocity_squared = (
                    neighbor["velocity"] ** 2
                )

                mass_fraction = (
                    velocity_squared /
                    total_v_squared
                )

                neighbor["mass"] = (
                    current_state[
                        "normalized_mass"
                    ]
                    * mass_fraction
                )

        # ====================================================
        # UPDATE NEIGHBORS
        # ====================================================

        for neighbor in reachable_neighbors:

            neighbor_cell = neighbor["cell"]

            neighbor_state = await get_cell_state(
                redis_client,
                neighbor_cell
            )

            if neighbor_state is None:
                continue

            candidate_arrival = (
                neighbor["arrival_time"]
            )

            old_arrival = (
                neighbor_state["arrival_time"]
            )

            # ------------------------------------------------
            # Only keep the earliest route
            # ------------------------------------------------

            if (
                old_arrival != -1
                and
                candidate_arrival >= old_arrival
            ):
                continue

            incoming_mass = neighbor["mass"]
            incoming_velocity = neighbor["velocity"]

            existing_mass = (
                neighbor_state[
                    "normalized_mass"
                ]
            )

            existing_velocity = (
                neighbor_state["velocity"]
            )

            # =================================================
            # COMBINE DEBRIS
            # =================================================

            if neighbor_state["debris_state"] == "STABLE":

                new_mass = incoming_mass
                new_velocity = incoming_velocity

            else:

                new_mass = (
                    existing_mass
                    +
                    incoming_mass
                )

                if new_mass > 0:

                    new_velocity = (
                        existing_mass *
                        existing_velocity
                        +
                        incoming_mass *
                        incoming_velocity
                    ) / new_mass

                else:

                    new_velocity = 0.0

            # ------------------------------------------------
            # Update state
            # ------------------------------------------------

            neighbor_state[
                "debris_state"
            ] = "FLOWING"

            neighbor_state[
                "normalized_mass"
            ] = new_mass

            neighbor_state[
                "velocity"
            ] = new_velocity

            neighbor_state[
                "specific_pe"
            ] = (
                neighbor_state["elevation"]
                * G
            )

            neighbor_state[
                "specific_ke"
            ] = (
                0.5 *
                new_velocity ** 2
            )

            neighbor_state[
                "arrival_time"
            ] = candidate_arrival

            # ------------------------------------------------
            # Save to Redis
            # ------------------------------------------------

            await save_cell_state(
                redis_client,
                neighbor_cell,
                neighbor_state
            )

            # ------------------------------------------------
            # Update earliest arrival
            # ------------------------------------------------

            earliest_arrival[
                neighbor_cell
            ] = candidate_arrival

            # ------------------------------------------------
            # Add to queue
            # ------------------------------------------------

            heapq.heappush(
                queue,
                (
                    candidate_arrival,
                    neighbor_cell
                )
            )

    return cells