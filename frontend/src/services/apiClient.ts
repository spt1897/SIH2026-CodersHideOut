import axios from 'axios';
import { useAuthStore } from '../store/useAuthStore';
import i18n from '../i18n';

export const apiClient = axios.create({
    baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8080',
    headers: {
        'Content-Type': 'application/json',
    },
});

apiClient.interceptors.request.use((config) => {
    const accessToken = useAuthStore.getState().accessToken;

    if (accessToken) {
        config.headers.Authorization = `Bearer ${accessToken}`;
    }

    config.headers['X-target-language'] = i18n.language;
    return config;
});

apiClient.interceptors.response.use(
    (response) => response,
    async (error) => {
        const originalRequest = error.config;

        if (error.response?.status === 401 && !originalRequest._retry) {
            originalRequest._retry = true;
            const refreshToken = useAuthStore.getState().refreshToken;

            if (refreshToken) {
                try {
                    const response = await axios.post(
                        `${apiClient.defaults.baseURL}/api/user/refresh`,
                        {},
                        {
                            headers: {
                                RefreshToken: refreshToken,
                            },
                        }
                    );

                    const { accessToken, refreshToken: newRefreshToken, role } = response.data;

                    useAuthStore.getState().updateTokens(accessToken, newRefreshToken, role);

                    originalRequest.headers.Authorization = `Bearer ${accessToken}`;
                    return apiClient(originalRequest);
                } catch (refreshError) {
                    useAuthStore.getState().logout();
                    return Promise.reject(refreshError);
                }
            }
        }

        return Promise.reject(error);
    }
);