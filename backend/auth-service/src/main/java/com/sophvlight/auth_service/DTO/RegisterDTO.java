package com.sophvlight.auth_service.DTO;

import jakarta.validation.Valid;
import jakarta.validation.constraints.Email;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotEmpty;
import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Pattern;
import jakarta.validation.constraints.Size;
import java.util.List;

public record RegisterDTO(
        @NotBlank(message = "Blank email") 
        @Email(message = "Invalid email format") 
        @Pattern(regexp = "^[A-Za-z0-9._%+-]+@(gov\\.in|nic\\.in)$", message = "Must be an official @gov.in or @nic.in domain")
        String email,

        @NotBlank(message = "Blank Password") 
        @Size(min = 8, max = 32, message = "Password must be between 8 and 32 characters") 
        String password,

        @NotBlank(message = "Name is blank")
        String name,

        @NotBlank(message = "Blank Ph no") 
        @Pattern(regexp = "^[0-9]{10}$", message = "Phone number must be exactly 10 digits")
        String phno,

        @NotBlank(message = "Blank designation")
        String designation,

        @NotBlank(message = "Empty Employee Id")
        String employeeId,

        @NotBlank(message = "Role is required")
        String role,

        @NotBlank(message = "Agency is required")
        String agency,

        @NotNull(message = "Jurisdiction cannot be null")
        @Valid
        JurisdictionDTO jurisdiction
) {
    public record JurisdictionDTO(
            @NotBlank(message = "State code is required")
            String stateCode,

            @NotEmpty(message = "At least one district code required")
            List<String> districtCodes,

            @NotEmpty(message = "At least one H3 cell resolution-6 required")
            List<String> h3Res6Cells
    ) {}
}