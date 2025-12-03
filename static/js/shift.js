/*
  PAYLOAD JSON SHIFT = {
    "Date": "date_string",
    "employees": [
      {
        "employeeId": "id_karyawan",
        "shift": "day/night",
        "clockIn": "waktu_check_in",
        "clockOut": "waktu_check_out"
      }
    ]
  }
*/

let employees = [];
let dayShift = [];
let nightShift = [];
let selectedDate = null;
let idShift = null;
const fetchEmployees = async () => {
  try {
    const res = await axios.get("/api/employees/all");
    employees = res.data.data || [];
    console.log("✅ Employees fetched:", employees);
  } catch (error) {
    console.error("❌ Error fetching employees:", error);
    webix.message({ type: "error", text: "Failed to fetch employees" });
  }
};

async function loadShiftByDate(date) {
  try {
    idShift = null;
    console.log("Selected date:", date);
    const res = await axios.get(`/api/attendance/${date}`);
    const shiftData = res.data.data?.employees || [];
    console.log("Shift data:", res.data.data);
    idShift = res.data.data?._id;

    dayShift = shiftData
      .filter((emp) => emp.shift.toLowerCase() === "day")
      .map((emp) => ({
        employeeId: emp.employeeId,
        name: emp.employee?.name || emp.employeeId,
        status: emp.status,
      }));

    nightShift = shiftData
      .filter((emp) => emp.shift.toLowerCase() === "night")
      .map((emp) => ({
        employeeId: emp.employeeId,
        name: emp.employee?.name || emp.employeeId,
        status: emp.status,
      }));

    renderDayShift();
    renderNightShift();
    renderSubmit();
  } catch (error) {
    console.error("❌ Error fetching shift:", error);
    webix.message({ type: "error", text: "Failed to fetch shift" });
  }
}

const renderEmployee = () => {
  const list = document.getElementById("employees-container");
  if (!list) return;

  if (employees.length === 0) {
    list.innerHTML = `<p class="text-gray-500 text-center py-4 text-sm">No employees found.</p>`;
    return;
  }

  list.innerHTML = employees
    .map(
      (user, i) => `
        <div class="relative inline-block text-left" id="userDropdown-${i}">
          <button 
            class="flex items-center justify-between w-full p-2 rounded-lg hover:bg-gray-100 transition"
            id="userMenuButton-${i}"
          >
            <div class="flex items-center space-x-2">
              <div class="w-7 h-7 md:w-8 md:h-8 rounded-full bg-[var(--sunrise-red)] shadow-md flex items-center justify-center text-white font-semibold text-sm">
                ${user.name.charAt(0).toUpperCase()}
              </div>
              <span class="text-xs md:text-sm font-medium text-[var(--text-primary)] truncate">${
                user.name
              }</span>
            </div>
            <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" md:width="16" md:height="16"
              viewBox="0 0 24 24" fill="none" stroke="currentColor"
              stroke-width="2" stroke-linecap="round" stroke-linejoin="round"
              class="text-[var(--text-secondary)] flex-shrink-0">
              <polyline points="6 9 12 15 18 9"></polyline>
            </svg>
          </button>

          <div 
            class="absolute left-0 mt-2 w-fit bg-white rounded-lg shadow-lg py-1 z-10 hidden"
            id="shiftDropdownMenu-${i}"
          >
            <a href="#" onclick="setShift('${
              user._id
            }', 'Day')" class="block px-3 md:px-4 py-2 text-xs md:text-sm text-blue-600 hover:bg-gray-100 flex items-center space-x-2">
              <img src="/static/photo/day.svg" alt="Day" class="w-3 h-3 md:w-4 md:h-4">
              <span>Set Day Shift</span>
            </a>
            <a href="#" onclick="setShift('${
              user._id
            }', 'Night')" class="block px-3 md:px-4 py-2 text-xs md:text-sm text-purple-600 hover:bg-gray-100 flex items-center space-x-2">
              <img src="/static/photo/night.svg" alt="Night" class="w-3 h-3 md:w-4 md:h-4">
              <span>Set Night Shift</span>
            </a>
          </div>
        </div>
      `
    )
    .join("");

  employees.forEach((user, i) => {
    const menuBtn = document.getElementById(`userMenuButton-${i}`);
    const dropdown = document.getElementById(`shiftDropdownMenu-${i}`);
    menuBtn.addEventListener("click", (e) => {
      e.stopPropagation();
      dropdown.classList.toggle("hidden");
    });
  });

  document.addEventListener("click", () => {
    employees.forEach((_, i) => {
      const dropdown = document.getElementById(`shiftDropdownMenu-${i}`);
      if (dropdown) dropdown.classList.add("hidden");
    });
  });
};

function setShift(employeeId, shiftType) {
  const emp = employees.find((e) => e._id === employeeId);
  if (!emp) return;

  if (shiftType === "Day") {
    if (!dayShift.some((e) => e.employeeId === employeeId)) {
      dayShift.push({ employeeId, name: emp.name });
      nightShift = nightShift.filter((e) => e.employeeId !== employeeId);
    }
  } else if (shiftType === "Night") {
    if (!nightShift.some((e) => e.employeeId === employeeId)) {
      nightShift.push({ employeeId, name: emp.name });
      dayShift = dayShift.filter((e) => e.employeeId !== employeeId);
    }
  }

  renderDayShift();
  renderNightShift();
  renderSubmit();
}

async function deleteShift(employeeId) {
  try {
    const res = await axios.put(
      `/api/attendance/remove/${idShift}`,
      {
        employeeId: employeeId,
      },
      { headers: { "Content-Type": "application/json" } }
    );
    webix.message({ type: "success", text: "Shift deleted successfully!" });
    await loadShiftByDate(selectedDate);
  } catch (err) {
    console.error("❌ Error deleting shift:", err);
    webix.message({ type: "error", text: "Failed to delete shift" });
  }
}

function renderDayShift() {
  const container = document.getElementById("dayShift-container");
  if (!container) return;

  if (dayShift.length === 0) {
    container.innerHTML = `<p class="text-gray-500 text-center py-4 text-sm">No employees in day shift.</p>`;
    return;
  }

  container.innerHTML = dayShift
    .map(
      (emp) => `
      <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center p-2 bg-gray-50 rounded-lg w-full gap-2">
        <div class="flex items-center space-x-2">
          <div class="w-7 h-7 md:w-8 md:h-8 rounded-full bg-[var(--morning-blue)] flex items-center justify-center text-white font-semibold text-sm flex-shrink-0">
            ${emp.name.charAt(0).toUpperCase()}
          </div>
          <span class="text-xs md:text-sm font-medium truncate">${
            emp.name
          }</span>
        </div>
        <div class="flex space-x-2 w-full sm:w-auto justify-end">
          <button onclick="setShift('${
            emp.employeeId
          }', 'Night')" class="text-purple-600 hover:underline text-xs md:text-sm whitespace-nowrap">Switch → 🌑</button>
          <button onclick="deleteShift('${
            emp.employeeId
          }')" class="text-red-600 hover:underline text-xs md:text-sm whitespace-nowrap">Delete</button>
        </div>
      </div>
    `
    )
    .join("");
}

function renderNightShift() {
  const container = document.getElementById("nightShift-container");
  if (!container) return;

  if (nightShift.length === 0) {
    container.innerHTML = `<p class="text-gray-500 text-center py-4 text-sm">No employees in night shift.</p>`;
    return;
  }

  container.innerHTML = nightShift
    .map(
      (emp) => `
      <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center p-2 bg-gray-50 rounded-lg w-full gap-2">
        <div class="flex items-center space-x-2">
          <div class="w-7 h-7 md:w-8 md:h-8 rounded-full bg-[var(--sunrise-red)] flex items-center justify-center text-white font-semibold text-sm flex-shrink-0">
            ${emp.name.charAt(0).toUpperCase()}
          </div>
          <span class="text-xs md:text-sm font-medium truncate">${
            emp.name
          }</span>
        </div>
        <div class="flex space-x-2 w-full sm:w-auto justify-end">
          <button onclick="setShift('${
            emp.employeeId
          }', 'Day')" class="text-blue-600 hover:underline text-xs md:text-sm whitespace-nowrap">Switch → ☀️</button>
          <button onclick="deleteShift('${
            emp.employeeId
          }')" class="text-red-600 hover:underline text-xs md:text-sm whitespace-nowrap">Delete</button>
        </div>
      </div>
    `
    )
    .join("");
}

const updateShift = async () => {
  try {
    const employeesPayload = [
      ...dayShift.map((emp) => ({
        employeeId: emp.employeeId,
        shift: "Day",
        clockIn: null,
        clockOut: null,
      })),
      ...nightShift.map((emp) => ({
        employeeId: emp.employeeId,
        shift: "Night",
        clockIn: null,
        clockOut: null,
      })),
    ];
    payload = {
      employees: employeesPayload,
    };
    const res = await axios.put(`/api/attendance/update/${idShift}`, payload, {
      headers: {
        "Content-Type": "application/json",
      },
    });
    if (!res.data.status) {
      return webix.message({
        type: "error",
        text: "Failed to add employee to shift",
      });
    }

    await loadShiftByDate(selectedDate);
    webix.message({ type: "success", text: "Employee added to shift!" });
  } catch (error) {
    console.error(error);
    webix.message({ type: "error", text: "Failed to add employee to shift" });
  }
};

async function submitShift() {
  try {
    if (!selectedDate) {
      webix.message({ type: "error", text: "Please select a date first" });
      return;
    }

    console.log("shift data", dayShift, nightShift);
    const employeesPayload = [
      ...dayShift.map((emp) => ({
        employeeId: emp.employeeId,
        shift: "Day",
        clockIn: null,
        clockOut: null,
      })),
      ...nightShift.map((emp) => ({
        employeeId: emp.employeeId,
        shift: "Night",
        clockIn: null,
        clockOut: null,
      })),
    ];

    const payload = { Date: selectedDate, employees: employeesPayload };

    console.log("📤 Final Payload:", payload);
    const res = await axios.post("/api/attendance/setShift", payload);
    console.log("📥 Response:", res.data);
    if (res?.data?.status === false) {
      const allErrors =
        Object.values(res.data.errors || {}).join("\n") || res.data.message;
      webix.message({ type: "error", text: allErrors });
      return;
    }

    webix.message({ type: "success", text: "Shift assigned successfully!" });
    await loadShiftByDate(selectedDate);
  } catch (error) {
    console.error("❌ Error submitting shift:", error.response.data.message);
    webix.message({ type: "error", text: "Failed to submit shift" });
  }
}

const renderSubmit = () => {
  const makeShiftBtn = document.getElementById("makeShiftBtn");
  if (!makeShiftBtn) return;

  makeShiftBtn.innerHTML = `
  <div class="text-xs md:text-sm">
    <p class="font-medium">Schedule Shift: <span class="font-bold">${
      selectedDate || "-"
    }</span></p>
    <p class="text-gray-600">Day: <span class="text-blue-600 font-semibold">${
      dayShift.length
    }</span> | Night: <span class="text-purple-600 font-semibold">${
    nightShift.length
  }</span></p>
  </div>
  
  ${
    idShift
      ? `<button class="gradient-btn text-white font-semibold px-3 md:px-4 py-2 rounded-xl hover:opacity-90 transition-all shadow-sm text-sm md:text-base whitespace-nowrap" onclick="updateShift()">Update Shift</button>`
      : `<button class="gradient-btn text-white font-semibold px-3 md:px-4 py-2 rounded-xl hover:opacity-90 transition-all shadow-sm text-sm md:text-base whitespace-nowrap" onclick="submitShift()">Save Shift</button>`
  }
  `;
};

document.addEventListener("DOMContentLoaded", async () => {
  await fetchEmployees();
  renderEmployee();

  const datePicker = document.getElementById("datePicker");
  if (datePicker) {
    const today = new Date();
    const formattedDate = today.toISOString().split("T")[0];
    datePicker.value = formattedDate;
    selectedDate = formattedDate;
    await loadShiftByDate(selectedDate);

    datePicker.addEventListener("change", async (e) => {
      selectedDate = e.target.value;
      await loadShiftByDate(selectedDate);
    });
  }

  renderSubmit();
});
