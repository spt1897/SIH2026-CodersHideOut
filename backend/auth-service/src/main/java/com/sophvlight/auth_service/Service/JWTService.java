package com.sophvlight.auth_service.Service;

import java.util.Base64;
import java.util.Date;
import java.util.HashMap;
import java.util.Map;
import java.util.function.Function;

import javax.crypto.SecretKey;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.security.core.userdetails.UserDetails;
import org.springframework.stereotype.Service;

import com.sophvlight.auth_service.Standards.Time;

import io.jsonwebtoken.Claims;
import io.jsonwebtoken.Jwts;
import io.jsonwebtoken.security.Keys;
@Service
public class JWTService {
    @Value("${software.jwt.access.secret}")
    private String secretKey;
    @Value("${software.jwt.access.life}")
    private long accessTokenLife;
    public String generateToken(String username){
        Map<String,Object> claims = new HashMap<>();
        return Jwts
                    .builder()
                    .claims()
                    .add(claims)
                    .issuedAt(Time.afterNow(0)).expiration(Time.afterNow(accessTokenLife))
                    .subject(username)
                    .and()
                    .signWith(getKey())
                    .compact();
    }
    private SecretKey getKey(){
        byte[] key = Base64.getDecoder().decode(secretKey);
        return Keys.hmacShaKeyFor(key);
    }
    public String extractUserName(String token) {
        return extractClaim(token,Claims::getSubject);
    }
    public boolean isValidToken(String token,UserDetails details) {
        final String userName = extractUserName(token);
        return (userName.equals(details.getUsername()) && !isTokenExpired(token));
    }
    public boolean isTokenExpired(String token){
        return extractExpiration(token).before(new Date());
    }
    public Claims extractAllClaims(String token){
        return Jwts
                    .parser()
                    .verifyWith(getKey())
                    .build()
                    .parseSignedClaims(token)
                    .getPayload();
    }
    public Date extractExpiration(String token){
        return extractClaim(token, Claims::getExpiration);
    }
    public <T> T extractClaim(String token,Function<Claims,T> claimResolver){
        final Claims claims= extractAllClaims(token);
        return claimResolver.apply(claims);
    }
}
