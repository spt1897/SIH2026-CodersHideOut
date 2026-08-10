package com.sophvlight.auth_service.Repo;

import java.util.Set;

import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.stereotype.Repository;

import com.sophvlight.auth_service.Model.Users;

import io.lettuce.core.dynamic.annotation.Param;
@Repository
public interface UserRepo extends JpaRepository<Users,Integer> {
    Users findByEmail(String email);

    Users findByUsername(String username);

    @Query("SELECT u.id FROM Users u WHERE u.username IN :usernames")
    Set<Integer> fetchAllIdsByUsernames(@Param("usernames") Set<String> usernames);

    @Query("SELECT u.username FROM Users u WHERE u.id IN :ids")
    Set<String> fetchAllUsernamesByIds(@Param("ids") Set<Integer> ids);
}
