package com.sophvlight.auth_service.Configuration;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.http.HttpMethod;
import org.springframework.security.authentication.AuthenticationManager;
import org.springframework.security.authentication.dao.DaoAuthenticationProvider;
import org.springframework.security.config.Customizer;
import org.springframework.security.config.annotation.authentication.configuration.AuthenticationConfiguration;
import org.springframework.security.config.annotation.web.builders.HttpSecurity;
import org.springframework.security.config.annotation.web.configuration.EnableWebSecurity;
import org.springframework.security.config.http.SessionCreationPolicy;
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;
import org.springframework.security.web.SecurityFilterChain;
import org.springframework.security.web.authentication.UsernamePasswordAuthenticationFilter;

import com.sophvlight.auth_service.Exception.DelegatedAuthenticationEntryPoint;
import com.sophvlight.auth_service.Filter.JWTFilter;
import com.sophvlight.auth_service.Service.UserService;
import com.sophvlight.auth_service.Standards.Links;



@Configuration
@EnableWebSecurity
public class SecurityConfig {
    private JWTFilter jwtfilter;
    private DelegatedAuthenticationEntryPoint authEntryPoint;
    @Autowired
    public SecurityConfig(JWTFilter jwtfilter,DelegatedAuthenticationEntryPoint authEntryPoint) {
        this.jwtfilter = jwtfilter;
        this.authEntryPoint=authEntryPoint;
    }

    @Bean
    public SecurityFilterChain securityFilterChain(HttpSecurity http) throws Exception  {
        return http
                .formLogin(e -> e.disable())
                .csrf(c -> c.disable())
                .oauth2Client(o->o.disable())
                .oauth2Login(o->o.disable())
                .cors(Customizer.withDefaults())
                .exceptionHandling(e -> e.authenticationEntryPoint(authEntryPoint))
                .sessionManagement(c -> c.sessionCreationPolicy(SessionCreationPolicy.STATELESS))
                .authorizeHttpRequests(c -> c
                        .requestMatchers(HttpMethod.OPTIONS, "/**")
                        .permitAll()
                        .requestMatchers(
                                Links.PUBLIC_ENDPOINTS)
                        .permitAll()
                        .anyRequest().authenticated())
                .addFilterBefore(jwtfilter, UsernamePasswordAuthenticationFilter.class)
                .build();
    }

    @Bean
    public DaoAuthenticationProvider authenticationProvider(UserService userService) {
        DaoAuthenticationProvider authProvider = new DaoAuthenticationProvider(userService);
        authProvider.setPasswordEncoder(passwordEncoder());
        return authProvider;
    }

    @Bean
    public BCryptPasswordEncoder passwordEncoder() {
        return new BCryptPasswordEncoder(10);
    }

    @Bean
    public AuthenticationManager authenticationManager(AuthenticationConfiguration config) {
        return config.getAuthenticationManager();
    }
}
