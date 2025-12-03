/**
 * Mendapatkan koordinat geolokasi pengguna saat ini dengan akurasi tinggi.
 *
 * Fungsi ini menggunakan Geolocation API browser untuk mengambil posisi geografis
 * pengguna secara real-time. Memerlukan izin akses lokasi dari pengguna dan
 * menggunakan opsi high accuracy untuk hasil yang lebih presisi.
 *
 * @returns {Promise<{latitude: number, longitude: number, accuracy: number}>}
 * Promise yang akan resolved dengan objek berisi:
 * - `latitude`: Lintang dari posisi pengguna (dalam derajat desimal).
 * - `longitude`: Bujur dari posisi pengguna (dalam derajat desimal).
 * - `accuracy`: Tingkat akurasi dari nilai latitude/longitude (dalam meter).
 *                Semakin kecil nilainya, semakin akurat posisinya.
 *
 * @throws {string}
 * Melempar error string jika:
 * - Geolocation tidak didukung oleh browser
 * - Permintaan geolocation gagal (timeout, izin ditolak, posisi tidak tersedia)
 * - User menolak memberikan izin akses lokasi
 *
 * @example
 * // Contoh penggunaan dasar
 * getCurrentLocation()
 *   .then((loc) => {
 *     console.log("Lokasi Anda:", loc);
 *     console.log(`Lat: ${loc.latitude}, Long: ${loc.longitude}`);
 *     console.log(`Akurasi: ${loc.accuracy} meter`);
 *   })
 *   .catch((err) => {
 *     console.error("Error mengambil lokasi:", err);
 *   });
 *
 * @example
 * // Contoh dengan async/await
 * async function tampilkanLokasi() {
 *   try {
 *     const lokasi = await getCurrentLocation();
 *     console.log(`Koordinat: ${lokasi.latitude}, ${lokasi.longitude}`);
 *   } catch (error) {
 *     console.error("Gagal mendapatkan lokasi:", error);
 *   }
 * }
 *
 * @note
 * - Fungsi ini memerlukan koneksi HTTPS atau localhost untuk bekerja
 * - Pengguna akan diminta izin akses lokasi saat pertama kali dipanggil
 * - enableHighAccuracy diset true untuk akurasi maksimal (konsumsi baterai lebih tinggi)
 * - Timeout diset 10 detik, jika melebihi waktu tersebut akan reject
 * - maximumAge = 0 memastikan posisi yang diambil selalu fresh/terbaru
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
