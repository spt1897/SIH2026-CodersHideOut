package com.sophvlight.auth_service.Filter;

import java.io.IOException;

import org.springframework.web.filter.OncePerRequestFilter;

import com.sophvlight.auth_service.Service.JWTService;
import com.sophvlight.auth_service.Service.UserService;

import io.jsonwebtoken.ExpiredJwtException;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.security.core.userdetails.UserDetails;
import org.springframework.security.web.authentication.WebAuthenticationDetailsSource;
import org.springframework.stereotype.Component;

import jakarta.servlet.FilterChain;
import jakarta.servlet.ServletException;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;

@Component
public class JWTFilter extends OncePerRequestFilter {
    private JWTService jwtService;
    private UserService userService;

    @Autowired
    public JWTFilter(JWTService jwtService, UserService userService) {
        this.jwtService = jwtService;
        this.userService = userService;
    }

    @Override
    protected void doFilterInternal(HttpServletRequest request, HttpServletResponse response, FilterChain filterChain)
            throws ServletException, IOException {
        if ("OPTIONS".equalsIgnoreCase(request.getMethod())) {
            response.setStatus(HttpServletResponse.SC_OK);
            return;
        }
        try {
            String authHeader = request.getHeader("Authorization");
            String token = null;
            String username = null;
            if (authHeader != null && authHeader.startsWith("Bearer ")) {
                token = authHeader.substring(7);
                username = jwtService.extractUserName(token);
                if (username != null && SecurityContextHolder.getContext().getAuthentication() == null) {
                    UserDetails details = userService.loadUserByUsername(username);
                    if (jwtService.isValidToken(token, details)) {
                        UsernamePasswordAuthenticationToken authToken = new UsernamePasswordAuthenticationToken(details,
                                null, details.getAuthorities());
                        authToken.setDetails(new WebAuthenticationDetailsSource().buildDetails(request));
                        SecurityContextHolder.getContext().setAuthentication(authToken);
                    }
                }
            }
        } catch (ExpiredJwtException e) {
            // Set an attribute to pass the message to our EntryPoint
            request.setAttribute("expired_exception_message", "Your token has expired. Please log in again.");
        } catch (Exception e) {
            request.setAttribute("expired_exception_message", "Invalid Token");
        }
        filterChain.doFilter(request, response);
    }

}
