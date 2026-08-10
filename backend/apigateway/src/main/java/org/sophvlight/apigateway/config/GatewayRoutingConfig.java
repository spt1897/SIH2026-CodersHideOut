package org.sophvlight.apigateway.config;

import org.springframework.cloud.gateway.route.RouteLocator;
import org.springframework.cloud.gateway.route.builder.RouteLocatorBuilder;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

@Configuration
public class GatewayRoutingConfig {

    @Bean
    public RouteLocator authRouteLocator(RouteLocatorBuilder builder) {
        return builder.routes()
            .route("auth-service-dynamic", r -> r
                .path("/user/**")
                .uri("lb://AUTH-SERVICE")) 
            .build();
    }
}
