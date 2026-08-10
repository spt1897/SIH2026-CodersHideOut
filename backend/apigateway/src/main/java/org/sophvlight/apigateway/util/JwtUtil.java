package org.sophvlight.apigateway.util;

import io.jsonwebtoken.Claims;
import io.jsonwebtoken.Jwts;
import io.jsonwebtoken.security.Keys;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;

import javax.crypto.SecretKey;
import java.util.Base64;
import java.util.Date;
import java.util.function.Function;

@Component
public class JwtUtil {
    @Value("${software.jwt.access.secret}")
    private String secretKey;

    private SecretKey getKey() {
        byte[] key = Base64.getDecoder().decode(secretKey);
        return Keys.hmacShaKeyFor(key);
    }

    public void validateToken(final String token) {
        Jwts.parser().verifyWith(getKey()).build().parseSignedClaims(token);
    }
    
    public String extractUsername(String token) {
        return extractClaim(token, Claims::getSubject); 
    }

    public Integer extractUserId(String token) {
        final Claims claims = Jwts.parser()
                .verifyWith(getKey())
                .build()
                .parseSignedClaims(token)
                .getPayload();
        
        return claims.get("userId", Integer.class);
    }

    public String extractRole(String token) {
        final Claims claims = Jwts.parser()
                .verifyWith(getKey())
                .build()
                .parseSignedClaims(token)
                .getPayload();
        
        return claims.get("role", String.class);
    }

    private <T> T extractClaim(String token, Function<Claims, T> claimsResolver) {
        final Claims claims = Jwts.parser().verifyWith(getKey()).build().parseSignedClaims(token).getPayload();
        return claimsResolver.apply(claims);
    }
}