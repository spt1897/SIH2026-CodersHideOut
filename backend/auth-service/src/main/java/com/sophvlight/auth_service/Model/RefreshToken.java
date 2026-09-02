package com.sophvlight.auth_service.Model;

import jakarta.persistence.Entity;
import jakarta.persistence.Id;
import jakarta.persistence.Table;

@Entity
@Table(name="refreshtoken")
public class RefreshToken {
    @Id
    private int userId;
    private String token;
    public RefreshToken() {
    }

    public RefreshToken(int userId, String token) {
        this.userId = userId;
        this.token = token;
    }
    
    public int getUserId() {
        return userId;
    }
    public void setUserId(int userId) {
        this.userId = userId;
    }
    public String getToken() {
        return token;
    }
    public void setToken(String token) {
        this.token = token;
    }

}
