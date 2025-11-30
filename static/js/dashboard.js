let branchRes;
let employeeRes;

const fetchDataDashboard = async () => {
  try {
    [branchRes, employeeRes] = await Promise.all([
      fetch("/api/branch", { method: "GET" }),
      fetch("/api/employees/all", { method: "GET" }),
    ]);

    if (!branchRes.ok || !employeeRes.ok) {
      throw new Error("Failed to fetch data");
    }

    const [branchData, employeeData] = await Promise.all([
      branchRes.json(),
      employeeRes.json(),
    ]);

    console.log("branchData", branchData);

    const branchCount = branchData?.data?.length || 0;
    const employeeCount = employeeData?.data?.length || 0;

    const data = [
      { key: "Branches", value: branchCount },
      { key: "Employees", value: employeeCount },
    ];

    const sortedEmployeeData = employeeData.data.sort((a, b) => {
      const dateA = new Date(a.createdAt || 0);
      const dateB = new Date(b.createdAt || 0);
      return dateB - dateA;
    });

    $$("employee-list").clearAll();
    $$("employee-list").parse(sortedEmployeeData);

    const sortedBranchData = branchData.data.sort((a, b) => {
      const dateA = new Date(a.createdAt || 0);
      const dateB = new Date(b.createdAt || 0);
      return dateB - dateA;
    });

    $$("branch-list").clearAll();
    $$("branch-list").parse(sortedBranchData);

    renderMap(branchData.data);
    return data;
  } catch (error) {
    console.error(error);
    webix.message({ type: "error", text: "Error fetching data" });
    return [];
  }
};

const renderDashboard = async () => {
  const dashboardContent = document.getElementById("dashboard-content");
  const data = await fetchDataDashboard();
  console.log("data", data);

  dashboardContent.innerHTML = data
    .map(
      (item) => `
        <div class="h-32 w-full flex flex-col items-center justify-center bg-white p-4 rounded-lg">
          <h3 class="text-lg font-semibold text-[var(--text-primary)]">${item.key}</h3>
          <p class="text-2xl font-bold text-[var(--arunika-gold)]">${item.value}</p>
        </div>
      `
    )
    .join("");
};

async function renderMap(branches) {
  let selectedCoordinates = [];
  let marker = null;

  if (!Array.isArray(selectedCoordinates) || selectedCoordinates.length < 2) {
    try {
      const loc = await getCurrentLocation();
      selectedCoordinates = [loc.longitude, loc.latitude];
      console.log("Using current location:", selectedCoordinates);
    } catch (err) {
      selectedCoordinates = [110.50179290614325, -7.325555980425633];
      console.warn("Using default location (Salatiga).");
    }
  }

  const mapContainer = document.getElementById("map-stores");
  if (!mapContainer) return;

  if (window.map) {
    try {
      window.map.remove();
      window.map = null;
    } catch (e) {
      console.warn("Error removing previous map:", e);
    }
  }

  const leafletCoords = [selectedCoordinates[1], selectedCoordinates[0]];

  window.map = L.map("map-stores", { attributionControl: true }).setView(
    leafletCoords,
    13
  );
  L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
    attribution:
      '&copy; <a href="https://www.openstreetmap.org/">OpenStreetMap</a>',
  }).addTo(window.map);

  marker = branches.map((branch) => {
    const coordinates = branch.geometry.coordinates;
    console.log("coordinate", coordinates);
    const marker = L.marker([coordinates[1], coordinates[0]]).addTo(window.map);
    marker.bindPopup(branch.name);
    return marker;
  });
}
