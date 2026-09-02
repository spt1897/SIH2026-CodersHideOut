async def calc_priority(probs,types,celldatas,trafficdatas):
    priorities = []
    for  prob,type, celldata, trafficdata in zip(probs,types,celldatas,trafficdatas):
        _,is_farmland,has_NH,has_SH,pop_d,building_d,road_d,rail_d,powerline,waterline,telecom,oilline = celldata

        freeflowspeed , curspeed ,roadclosed= trafficdata["freeFlowSpeed"] , trafficdata["currentSpeed"],trafficdata["roadClosure"]

        trafficfactor =max(0,1-(curspeed/freeflowspeed)) if not roadclosed else 0

        conn_score = 0.4*has_NH + 0.2*has_SH + 0.25*min(1,road_d/5) + 0.15*min(1,rail_d/2)

        human_exposure = 0.45*min(1,pop_d/1) + 0.25*min(1,building_d/3) + 0.3*trafficfactor

        critical_lifelines = 0.35*min(1,powerline/3) + 0.25*min(1,waterline/3)+0.25*min(1,telecom/3) +0.15*min(1,oilline/3)

        if type=="predicted":
            priority_score = 35*prob + 25*human_exposure+20*conn_score+15*critical_lifelines+5*is_farmland
        else:
            priority_score = 40 * human_exposure +30*conn_score+20*critical_lifelines+10*is_farmland
            if type=="projected": priority_score+=100
            elif type=="confirmed": priority_score+=200

        priorities.append(priority_score)

    return priorities