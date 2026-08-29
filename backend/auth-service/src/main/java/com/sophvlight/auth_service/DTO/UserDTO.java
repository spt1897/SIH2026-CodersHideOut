package com.sophvlight.auth_service.DTO;

import org.hibernate.validator.constraints.Length;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Pattern;

public record UserDTO(
        @NotBlank(message = "Login identifier cannot be blank")
        @Pattern(
            regexp = "^([A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,}|[0-9]{10})$", 
            message = "Must be a valid email or a 10-digit phone number"
        )
        String identifier,

        @NotBlank(message = "Blank Password")
        @Length(max = 20, message="Password must not be longer than 20 characters")
        String password
) {
}