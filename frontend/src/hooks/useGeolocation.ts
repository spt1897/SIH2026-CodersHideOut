import { useState } from 'react';

export function useGeolocation() {
  const [coordinates, setCoordinates] = useState<{ lat: number; lng: number; accuracy: number } | null>(null);
  const [geoError, setGeoError] = useState<string | null>(null);
  const [isLocating, setIsLocating] = useState<boolean>(false);

  const fetchLocation = () => {
    setIsLocating(true);
    setGeoError(null);

    if (!navigator.geolocation) {
      setGeoError("Geolocation is not supported by your browser or device.");
      setIsLocating(false);
      return;
    }

    navigator.geolocation.getCurrentPosition(
      (position) => {
        setCoordinates({
          lat: position.coords.latitude,
          lng: position.coords.longitude,
          accuracy: position.coords.accuracy, // Good to know if the GPS signal is weak
        });
        setIsLocating(false);
      },
      (error) => {
        setGeoError(error.message);
        setIsLocating(false);
      },
      { 
        enableHighAccuracy: true, // Forces GPS chip activation on mobile
        timeout: 10000,           // Give up after 10 seconds
        maximumAge: 0             // Don't use a cached location
      }
    );
  };

  return { coordinates, geoError, isLocating, fetchLocation };
}