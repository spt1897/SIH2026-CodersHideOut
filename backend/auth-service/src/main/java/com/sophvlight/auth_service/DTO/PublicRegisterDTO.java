package com.sophvlight.auth_service.DTO;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Pattern;

public record PublicRegisterDTO(
        @NotBlank(message = "Mobile number is required")
        @Pattern(regexp = "^[0-9]{10}$", message = "Phone number must be exactly 10 digits")
        String phno,

        String name, // Optional

        @NotBlank(message = "Password/PIN is required to secure the account")
        String password,

        @NotBlank(message = "Home location (H3 cell or Pincode) is required")
        String homeLocation,

        @NotBlank(message = "Preferred language is required")
        String preferredLanguage
) {}