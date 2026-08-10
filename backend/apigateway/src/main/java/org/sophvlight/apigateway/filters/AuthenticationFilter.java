package org.sophvlight.apigateway.filters;

import org.springframework.http.HttpHeaders;
import org.sophvlight.apigateway.util.JwtUtil;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.cloud.gateway.filter.GatewayFilter;
import org.springframework.cloud.gateway.filter.factory.AbstractGatewayFilterFactory;
import org.springframework.http.HttpStatus;
import org.springframework.stereotype.Component;
import org.springframework.web.server.ResponseStatusException;

@Component
public class AuthenticationFilter extends AbstractGatewayFilterFactory<AuthenticationFilter.Config> {

    @Autowired
    private JwtUtil jwtUtil;

    @Autowired
    private RouteValidator validator;

    public AuthenticationFilter() {
        super(Config.class);
    }

    @Override
    public GatewayFilter apply(Config config) {
        return ((exchange, chain) -> {
            if (validator.isSecured.test(exchange.getRequest())) {
                
                String authHeader = exchange.getRequest().getHeaders().getFirst(HttpHeaders.AUTHORIZATION);

                if (authHeader == null) {
                    throw new ResponseStatusException(HttpStatus.UNAUTHORIZED, "Missing authorization header");
                }

                if (authHeader.startsWith("Bearer ")) {
                    authHeader = authHeader.substring(7);
                }

                try {
                    jwtUtil.validateToken(authHeader);
                    
                    String username = jwtUtil.extractUsername(authHeader);
                    Integer userId = jwtUtil.extractUserId(authHeader);
                    String role = jwtUtil.extractRole(authHeader);

                    exchange.getRequest().mutate().header("X-Auth-Username", username).build();
                    exchange.getRequest().mutate().header("X-Auth-UserId", userId.toString()).build();
                    exchange.getRequest().mutate().header("X-Auth-Role", role).build();
                } catch (Exception e) {
                    throw new ResponseStatusException(HttpStatus.UNAUTHORIZED, "Unauthorized access");
                }
            }
            return chain.filter(exchange);
        });
    }

    public static class Config { }
}