package org.sophvlight.apigateway.filters;

import org.springframework.cloud.gateway.filter.GatewayFilter;
import org.springframework.cloud.gateway.filter.factory.AbstractGatewayFilterFactory;
import org.springframework.data.redis.core.ReactiveStringRedisTemplate;
import org.springframework.http.HttpStatus;
import org.springframework.stereotype.Component;
import org.springframework.web.server.ResponseStatusException;
import reactor.core.publisher.Mono;

@Component
public class ApiKeyFilter extends AbstractGatewayFilterFactory<ApiKeyFilter.Config> {

    private final ReactiveStringRedisTemplate redisTemplate;
    private final RouteValidator validator;

    public ApiKeyFilter(ReactiveStringRedisTemplate redisTemplate, RouteValidator validator) {
        super(Config.class);
        this.redisTemplate = redisTemplate;
        this.validator = validator;
    }

    @Override
    public GatewayFilter apply(Config config) {
        return (exchange, chain) -> {
            
            if (validator.isSecured.test(exchange.getRequest())) {
                String incomingApiKey = exchange.getRequest().getHeaders().getFirst("X-API-KEY");

                if (incomingApiKey == null || incomingApiKey.isBlank()) {
                    return Mono.error(new ResponseStatusException(HttpStatus.UNAUTHORIZED, "Missing X-API-KEY header"));
                }

                return redisTemplate.hasKey("apikey:" + incomingApiKey)
                        .flatMap(exists -> {
                            if (Boolean.FALSE.equals(exists)) {
                                return Mono.error(new ResponseStatusException(HttpStatus.UNAUTHORIZED, "Invalid API Key"));
                            }
                            return chain.filter(exchange);
                        });
            }
            return chain.filter(exchange);
        };
    }

    public static class Config { }
}