package com.sophvlight.auth_service.DTO;

public class TokenDTO {
    private String accessToken;
    private String refreshToken;
    private String role;
    public TokenDTO(String accessToken, String refreshToken,String role) {
        this.accessToken = accessToken;
        this.refreshToken = refreshToken;
        this.role=role;
    }
    public String getAccessToken() {
        return accessToken;
    }
    public String getRefreshToken() {
        return refreshToken;
    }
    public String getRole() {
        return role;
    }
}
