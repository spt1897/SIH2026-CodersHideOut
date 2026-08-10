package org.sophvlight.apigateway.config;

import org.sophvlight.apigateway.filters.AuthenticationFilter;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.cloud.gateway.route.RouteLocator;
import org.springframework.cloud.gateway.route.builder.RouteLocatorBuilder;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

@Configuration
public class GatewayRoutingConfig {

    private AuthenticationFilter filter;

    @Autowired
    public GatewayRoutingConfig(AuthenticationFilter filter) {
        this.filter = filter;
    }

    @Bean
    public RouteLocator authRouteLocator(RouteLocatorBuilder builder) {
        return builder.routes()
            .route("auth-service-dynamic", r -> r
                .path("/user/**")
                .uri("lb://AUTH-SERVICE")) 
            .build();
    }
}
