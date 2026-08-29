package com.sophvlight.auth_service.Model;

import java.time.LocalDateTime;

import com.sophvlight.auth_service.Standards.Role;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;
import jakarta.persistence.Table;

@Entity
@Table(name="user_data")
public class Users {
    
    @Id
    @GeneratedValue(strategy = GenerationType.AUTO)
    private int id;
    
    @Column(unique = true, nullable = false)
    private String email;
    
    private String phno;
    private String password;
    private String role;
    
    // New Profile Fields
    private String name;
    private String designation;
    
    @Column(unique = true)
    private String employeeId;
    
    private String agency;
    
    // New Jurisdiction Fields
    private String stateCode;
    
    @Column(columnDefinition = "TEXT")
    private String districtCodes; // Store as comma-separated string
    
    @Column(columnDefinition = "TEXT")
    private String h3Res6Cells; // Store as comma-separated string
    
    private LocalDateTime createdAt;
    private LocalDateTime lastLogin;

    private String preferredLanguage;

    public String getPreferredLanguage() { return preferredLanguage; }
    public void setPreferredLanguage(String preferredLanguage) { this.preferredLanguage = preferredLanguage; }

    public Users(){}

    // Updated Constructor for full onboarding mapping
    public Users(String email, String phno, String password, String role, 
                 String name, String designation, String employeeId, 
                 String agency, String stateCode, String districtCodes, String h3Res6Cells) {
        this.email = email;
        this.phno = phno;
        this.password = password;
        this.name = name;
        this.designation = designation;
        this.employeeId = employeeId;
        this.agency = agency;
        this.stateCode = stateCode;
        this.districtCodes = districtCodes;
        this.h3Res6Cells = h3Res6Cells;
        
        switch (role.toUpperCase()) {
            case Role.PLATFORM_OPERATOR:
                this.role=Role.PLATFORM_OPERATOR;
                break;
            case Role.INFRASTRUCTURE_AUTHORITIES:
                this.role=Role.INFRASTRUCTURE_AUTHORITIES;
                break;
            case Role.FIELD_OFFICER:
                this.role=Role.FIELD_OFFICER;
                break;
            case Role.EMERGENCY_RESPONSE:
                this.role=Role.EMERGENCY_RESPONSE;
                break;
            case Role.DISASTER_MANAGER:
                this.role=Role.DISASTER_MANAGER;
                break;
            default:
                this.role=Role.USER;
                break;
        }
    }

    // Existing Getters & Setters
    public int getId() { return id; }
    
    public String getPhno() { return phno; }
    public void setPhno(String phno) { this.phno = phno; }
    
    public String getEmail() { return email; }
    public void setEmail(String email) { this.email = email; }
    
    public String getPassword() { return password; }
    public void setPassword(String password) { this.password = password; }
    
    public LocalDateTime getCreatedAt() { return createdAt; }
    public void setCreatedAt(LocalDateTime createdAt) { this.createdAt = createdAt; }
    
    public LocalDateTime getLastLogin() { return lastLogin; }
    public void setLastLogin(LocalDateTime lastLogin) { this.lastLogin = lastLogin; }
    
    public String getRole() { return role; }
    public void setRole(String role) { this.role = role; }

    // New Getters & Setters
    public String getName() { return name; }
    public void setName(String name) { this.name = name; }

    public String getDesignation() { return designation; }
    public void setDesignation(String designation) { this.designation = designation; }

    public String getEmployeeId() { return employeeId; }
    public void setEmployeeId(String employeeId) { this.employeeId = employeeId; }

    public String getAgency() { return agency; }
    public void setAgency(String agency) { this.agency = agency; }

    public String getStateCode() { return stateCode; }
    public void setStateCode(String stateCode) { this.stateCode = stateCode; }

    public String getDistrictCodes() { return districtCodes; }
    public void setDistrictCodes(String districtCodes) { this.districtCodes = districtCodes; }

    public String getH3Res6Cells() { return h3Res6Cells; }
    public void setH3Res6Cells(String h3Res6Cells) { this.h3Res6Cells = h3Res6Cells; }
}