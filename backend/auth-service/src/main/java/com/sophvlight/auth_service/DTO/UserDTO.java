package com.sophvlight.auth_service.DTO;

import org.hibernate.validator.constraints.Length;

import jakarta.validation.constraints.Email;
import jakarta.validation.constraints.NotBlank;

public record UserDTO(
@NotBlank(message = "Blank email")
@Email(message = "Invalid email format")
String email,
@NotBlank(message = "Blank Password")
@Length(max = 20, message="Password must not be longer than 20 letters")
String password,
@NotBlank(message = "Blank Username")
String username) {
    
}
