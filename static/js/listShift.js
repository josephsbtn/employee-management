let employees = [];
let selectedMonth = null;
let currentShiftData = null;
let currentShiftId = null;
let isRequested = false;

const clockIn = async () => {
  const btn = document.getElementById("btnClockIn");
  try {
    if (isRequested) {
      webix.alert("Please wait, your request is being processed.");
      return;
    }
    isRequested = true;
    webix.message("Clocking in...");

    btn.classList.add("opacity-50", "cursor-not-allowed");
    btn.disabled = true;

    const currentPosition = await getCurrentLocation();
    console.log("currentPosition", currentPosition);
    const locationPayload = {
      type: "Point",
      coordinates: [currentPosition.longitude, currentPosition.latitude],
    };

    const res = await axios.post(
      `/api/attendance/clockIn`,
      {
        geometry: locationPayload,
        shiftId: currentShiftId,
      },
      {
        headers: {
          "Content-Type": "application/json",
        },
      }
    );

    if (res.data.status) {
      await renderSchedule(selectedMonth);
      await loadCurrentShift();
      console.log("Clock in successful!");
      isRequested = false;

      btn.classList.remove("opacity-50", "cursor-not-allowed");
      btn.disabled = false;
      return webix.message({ type: "success", text: "Clock in successful!" });
    }
    isRequested = false;
    btn.disabled = false;
    btn.classList.remove("opacity-50", "cursor-not-allowed");
    console.log("Clock in failed:", res.data);
    webix.message({
      type: "error",
      text: "Failed to clock in. " + res.data.message,
    });
    console.error("❌ Clock in failed:", res.data.message);
  } catch (error) {
    isRequested = false;
    console.error("❌ Error clocking in:", error);
    btn.classList.remove("opacity-50", "cursor-not-allowed");
    btn.disabled = false;
    webix.message({
      type: "error",
      text: "Failed to clock in. Something went wrong",
    });
  }
};

const clockOut = async () => {
  if (isRequested) {
    webix.alert("Please wait, your request is being processed.");
    return;
  }
  isRequested = true;
  const btn = document.getElementById("btnClockOut");
  try {
    btn.classList.add("opacity-50", "cursor-not-allowed");
    btn.disabled = true;
    const currentPosition = await getCurrentLocation();
    const locationPayload = {
      type: "Point",
      coordinates: [currentPosition.longitude, currentPosition.latitude],
    };

    const res = await axios.post(
      "/api/attendance/clockOut",
      {
        shiftId: currentShiftId,
        geometry: locationPayload,
      },
      {
        headers: {
          "Content-Type": "application/json",
        },
      }
    );

    isRequested = false;
    if (res?.data?.status) {
      await renderSchedule(selectedMonth);
      await loadCurrentShift();
      btn.classList.remove("opacity-50", "cursor-not-allowed");
      btn.disabled = false;
      return webix.message({ type: "success", text: "Clock out successful!" });
    }
    console.error("❌ Clock out failed:", res.data.message);
    webix.message({
      type: "error",
      text: "Failed to clock out. " + res.data.message,
    });
    btn.classList.remove("opacity-50", "cursor-not-allowed");
    btn.disabled = false;
  } catch (error) {
    isRequested = false;
    console.error("❌ Error clocking out:", error);
    webix.message({ type: "error", text: "Failed to clock out." });
    btn.classList.remove("opacity-50", "cursor-not-allowed");
    btn.disabled = false;
  }
};

const fetchEmployees = async () => {
  try {
    const res = await axios.get("/api/employees/all");
    employees = res.data.data || [];
  } catch (error) {
    console.error("❌ Error fetching employees:", error);
    webix.message({ type: "error", text: "Failed to fetch employees" });
  }
};

const renderEmployee = () => {
  const employeeCount = document.getElementById("employeesCount");
  if (employeeCount) {
    employeeCount.textContent = employees.length;
  }
  console.log("👥 Rendered employees:", employees);
};

const loadMonthlyShifts = async () => {
  const container = document.getElementById("shiftList");
  if (!container) return;

  try {
    const res = await axios.get(
      `/api/attendance/getMonthlyShifts/${selectedMonth}`
    );

    const shifts = res.data.data || [];

    if (shifts.length < 1) {
      container.innerHTML = `
        <div class="col-span-full">
          <h3 class="text-center text-gray-500 py-8">
            No shifts found for ${selectedMonth}
          </h3>
        </div>`;
      return;
    }

    loadCurrentShift();

    container.innerHTML = shifts
      .map((shift) => {
        const date = new Date(shift.Date);
        const formattedDate = date.toLocaleDateString("en-US", {
          year: "numeric",
          month: "long",
          day: "numeric",
        });

        const employeeList = (shift.employees || [])
          .map((emp) => {
            const empName = emp.employee?.name || "Unknown";
            const statusClass =
              emp.status === "present"
                ? "text-green-600 bg-green-50"
                : emp.status === "late"
                ? "text-yellow-600 bg-yellow-50"
                : "text-gray-400 bg-gray-50";
            const shiftClass =
              emp.shift === "Day"
                ? "bg-[var(--morning-blue)] text-[var(--pure-white)]"
                : emp.shift === "Night"
                ? "bg-[var(--calm-blue)] text-[var(--pure-white)]"
                : "bg-[var(--smoky-gray)] text-[var(--pure-white)]";
            return `
              <div class="grid grid-cols-3 items-center text-xs px-3 py-2 mb-1 border border-gray-100 rounded-lg shadow-sm hover:shadow transition">
                <p class="font-medium text-[var(--text-primary)]">${empName}</p>
                <p class="text-center ${shiftClass} rounded-lg px-2 py-1">${
              emp.shift || "N/A"
            }</p>
                <p class="${statusClass} text-center font-semibold px-2 py-1 rounded-lg capitalize">
                  ${emp.status || "-"}
                </p>
              </div>`;
          })
          .join("");

        return `
          <div class="flex flex-col gap-1 items-start p-3 rounded-lg shadow bg-white border border-gray-200 w-full">
            <p class="text-gray-700 font-semibold text-xs mb-2">${formattedDate}</p>
            <div class="w-full">${
              employeeList ||
              "<p class='text-gray-400 text-xs'>No employees assigned</p>"
            }</div>
          </div>
        `;
      })
      .join("");
  } catch (error) {
    console.error("❌ Failed to fetch shifts:", error);
    webix.message({ type: "error", text: "Failed to fetch shift data" });
    container.innerHTML = `
      <div class="col-span-full">
        <p class="text-center text-red-500 py-8">Error loading shifts</p>
      </div>`;
  }
};

const loadPresentLate = async () => {
  try {
    const [res, leave] = await Promise.all([
      axios.get(`/api/attendance/getMonthlySummary/${selectedMonth}`),
      axios.get("/api/annualRequest/list-manager"),
    ]);

    console.log("✅ Monthly summary:", res.data.data);
    const presentCount = res.data.data?.presentCount || 0;
    const lateCount = res.data.data?.lateCount || 0;
    const request = leave.data.data || [];
    const requestCount = request.filter(
      (req) => req.status === "pending"
    ).length;

    const presentElement = document.getElementById("presentCount");
    const lateElement = document.getElementById("lateCount");
    const requestsCount = document.getElementById("requestCount");

    if (presentElement && lateElement && requestsCount) {
      presentElement.textContent = presentCount;
      lateElement.textContent = lateCount;
      requestsCount.textContent = requestCount;
    }
  } catch (error) {
    console.error("❌ Failed to fetch summary:", error);
    webix.message({
      type: "error",
      text: "Failed to fetch attendance summary",
    });
  }
};

const renderAttendance = () => {
  try {
    const container = document.getElementById("attendance-card");
    if (!container) return;

    console.log("currentShiftData", currentShiftData);

    container.innerHTML = `
      <h3 class="text-sm text-gray-500 font-bold">Today Attendance</h3>
      <p class="text-base font-bold text-[var(--morning-blue)]">${new Date().toLocaleDateString(
        "en-US",
        {
          year: "numeric",
          month: "short",
          day: "numeric",
        }
      )}</p>

      ${
        currentShiftData.myShift[0].status === "absent"
          ? `<button
                id="btnClockIn"
                class="gradient-btn text-white px-4 md:px-5 py-2.5 md:py-2 rounded-lg text-sm md:text-base font-medium hover:opacity-90 transition-all w-full sm:w-auto"
                onclick="clockIn()"
              >
                🕐 Clock In
              </button>`
          : `<button
                id="btnClockOut"
                class="gradient-btn text-white px-4 md:px-5 py-2.5 md:py-2 rounded-lg text-sm md:text-base font-medium hover:opacity-90 transition-all w-full sm:w-auto"
                onclick="clockOut()"
              >
                🕑 Clock Out
              </button>`
      }
    `;
  } catch (error) {
    console.error("❌ Failed to render attendance:", error);
    webix.message({ type: "error", text: "Failed to render attendance card" });
  }
};

const loadCurrentShift = async () => {
  const user = await currentUser();
  try {
    const res = await axios.get(
      `/api/attendance/getMonthlyShifts/${selectedMonth}`
    );
    const shifts = res.data.data || [];

    const todayShift = shifts.find((shift) => {
      const date = new Date(shift.Date);
      const today = new Date();
      return (
        date.getDate() === today.getDate() &&
        date.getMonth() === today.getMonth() &&
        date.getFullYear() === today.getFullYear()
      );
    });

    if (todayShift) {
      const myShift = todayShift.employees.filter((emp) => {
        return emp.employeeId === user.id;
      });

      currentShiftData = {
        shiftId: todayShift._id,
        myShift,
      };
      renderAttendance();
      currentShiftId = todayShift._id;
    }
  } catch (error) {
    console.error("❌ Failed to load current shift:", error);
  }
};

const renderSchedule = async () => {
  try {
    const monthPicker = document.getElementById("monthPicker");
    if (monthPicker) {
      const now = new Date();
      const year = now.getFullYear();
      const month = String(now.getMonth() + 1).padStart(2, "0");
      const formattedMonth = `${year}-${month}`;

      monthPicker.value = formattedMonth;
      selectedMonth = formattedMonth;

      console.log("📅 Selected month:", selectedMonth);

      await loadMonthlyShifts();
      await loadPresentLate();

      monthPicker.addEventListener("change", async (e) => {
        selectedMonth = e.target.value;
        await loadMonthlyShifts();
        await loadPresentLate();
      });
    }
  } catch (error) {
    console.error("❌ Failed to render schedule:", error);
    webix.message({ type: "error", text: "Failed to render schedule" });
  }
};
