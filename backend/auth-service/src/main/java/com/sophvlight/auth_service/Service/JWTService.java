package com.sophvlight.auth_service.Service;

import java.util.Arrays;
import java.util.Base64;
import java.util.Date;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.function.Function;

import javax.crypto.SecretKey;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.security.core.userdetails.UserDetails;
import org.springframework.stereotype.Service;

import com.sophvlight.auth_service.Model.Users; // Import Users instead of RegisterDTO
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

    // CHANGED: Accepts the Users database entity
    public String generateToken(String subjectId, Users userDetails, List<String> permissions) {
        Map<String,Object> claims = new HashMap<>();
        
        // Use getters from the Users entity
        claims.put("userId",userDetails.getId());
        claims.put("name", userDetails.getName());
        claims.put("role", userDetails.getRole());
        claims.put("agency", userDetails.getAgency());
        
        // Nested Jurisdiction Map
        Map<String, Object> jurisdiction = new HashMap<>();
        jurisdiction.put("state_code", userDetails.getStateCode());
        
        // Safely split the comma-separated strings back into arrays
        List<String> districtCodes = (userDetails.getDistrictCodes() != null && !userDetails.getDistrictCodes().isEmpty()) 
            ? Arrays.asList(userDetails.getDistrictCodes().split(",")) 
            : List.of();
            
        List<String> h3Cells = (userDetails.getH3Res6Cells() != null && !userDetails.getH3Res6Cells().isEmpty()) 
            ? Arrays.asList(userDetails.getH3Res6Cells().split(",")) 
            : List.of();

        jurisdiction.put("district_codes", districtCodes); 
        jurisdiction.put("h3_res6_cells", h3Cells);
        claims.put("jurisdiction", jurisdiction);
        
        // Permissions Array
        claims.put("permissions", permissions);

        return Jwts
                    .builder()
                    .claims()
                    .add(claims)
                    .issuedAt(Time.afterNow(0))
                    .expiration(Time.afterNow(accessTokenLife))
                    .subject(subjectId) // e.g. "user_usr_98410294"
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