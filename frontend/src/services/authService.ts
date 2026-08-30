import { apiClient } from './apiClient';

export interface AuthResponse {
    accessToken: string;
    refreshToken: string;
    role: string;
}

export interface LoginPayload {
    email: string;
    password: string;
}

export const authService = {

    register: async (payload: LoginPayload): Promise<void> => {
        await apiClient.post('/api/user/register', payload);
    },

    login: async (payload: LoginPayload): Promise<AuthResponse> => {
        const response = await apiClient.post<AuthResponse>('/api/user/login', payload);
        return response.data;
    },

    logout: async (): Promise<void> => {
        await apiClient.post('/api/user/logout');
    },
};