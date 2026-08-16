package org.sophvlight.apigateway.config;

import org.sophvlight.apigateway.filters.ApiKeyFilter;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.cloud.gateway.filter.ratelimit.KeyResolver;
import org.springframework.cloud.gateway.filter.ratelimit.RedisRateLimiter;
import org.springframework.cloud.gateway.route.RouteLocator;
import org.springframework.cloud.gateway.route.builder.RouteLocatorBuilder;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

@Configuration
public class GatewayRoutingConfig {

    private ApiKeyFilter filter;
    private KeyResolver keyResolver;

    @Value("${cache.replenish-rate:10}")
    private int defaultReplenishRate;

    @Value("${cache.burst-capacity:10}")
    private long defaultBurstCapacity;

    @Autowired
    public GatewayRoutingConfig(ApiKeyFilter filter, KeyResolver keyResolver) {
        this.filter = filter;
        this.keyResolver = keyResolver;
    }

    @Bean
    public RedisRateLimiter redisRateLimiter(){
        return new RedisRateLimiter(defaultReplenishRate, defaultBurstCapacity,1);
    }

    @Bean
    public RouteLocator routeLocator(RouteLocatorBuilder builder) {
        return builder.routes()
            .route("auth-service-dynamic", r -> r
                .path("/user/**")
                .filters(f -> f 
                    .filter(filter.apply(new ApiKeyFilter.Config()))
                    .requestRateLimiter(c -> c
                        .setRateLimiter(redisRateLimiter())
                        .setKeyResolver(keyResolver)
                    )
                ) 
                .uri("lb://AUTH-SERVICE"))
            .build();
    }
}
