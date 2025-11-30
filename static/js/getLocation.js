/**
 * Get the user's current geolocation coordinates with high accuracy.
 *
 * @returns {Promise<{latitude: number, longitude: number, accuracy: number}>}
 * A promise that resolves with an object containing:
 * - `latitude`: The latitude of the user's position (in decimal degrees).
 * - `longitude`: The longitude of the user's position (in decimal degrees).
 * - `accuracy`: The accuracy level of the latitude/longitude values (in meters).
 *
 * @throws {string}
 * Throws an error string if geolocation is not supported by the browser
 * or if the geolocation request fails (timeout, permission denied, etc.).
 *
 * @example
 * getCurrentLocation()
 *   .then((loc) => console.log("Your location:", loc))
 *   .catch((err) => console.error("Location error:", err));
 */

async function getCurrentLocation() {
  return new Promise((resolve, reject) => {
    if (!navigator.geolocation) {
      reject("Geolocation not supported.");
    } else {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          resolve({
            latitude: position.coords.latitude,
            longitude: position.coords.longitude,
            accuracy: position.coords.accuracy,
          });
        },
        (error) => reject(error.message),
        {
          enableHighAccuracy: true,
          timeout: 10000,
          maximumAge: 0,
        }
      );
    }
  });
}
