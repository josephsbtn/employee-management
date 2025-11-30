let employees = [];
let selectedMonth = null;

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
    console.log("✅ Shift data:", res.data.data);

    const shifts = res.data.data || [];

    if (shifts.length < 1) {
      container.innerHTML = `
        <h3 class="text-center text-gray-500 h-full flex items-center justify-center">
          No shifts found for ${selectedMonth}
        </h3>`;
      return;
    }

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
            console.log("emp", emp);
            console.log("shift", shift);
            const empName = emp.employee.name;
            const statusClass =
              emp.status === "present"
                ? "text-green-600 bg-green-50"
                : emp.status === "late"
                ? "text-yellow-600 bg-yellow-50"
                : "text-gray-400 bg-gray-50";
            const shiftClass =
              emp.shift === "Day"
                ? "bg-[var(--morning-blue)] text-[var(--pure-white)]"
                : "bg-[var(--sunrise-red)] text-[var(--pure-white)]";
            return `
      <div class="grid grid-cols-3 items-center text-xs px-3 py-2 mb-1 border border-gray-100 rounded-lg shadow-sm hover:shadow transition">
        <p class="font-medium text-[var(--text-primary)]">${empName}</p>
        <p class="text-gray-500 text-center ${shiftClass} rounded-lg ">${
              emp.shift
            }</p>
        <p class="${statusClass} text-center font-semibold px-2 py-1 rounded-lg capitalize">
          ${emp.status || "-"}
        </p>
      </div>`;
          })
          .join("");

        return `
        <div class="flex flex-col gap-1 items-start p-3 rounded-lg shadow bg-white border border-gray-200 w-full">
          <p class="text-gray-700 font-semibold text-xs">${formattedDate}</p>
          <div class="w-full">${
            employeeList || "<p class='text-gray-400'>No employees</p>"
          }</div>
        </div>
      `;
      })
      .join("");
  } catch (error) {
    console.error("❌ Failed to fetch shift:", error);
    webix.message({ type: "error", text: "Failed to fetch shift data" });
  }
};

const loadPresentLate = async () => {
  try {
    const [res, leave] = await Promise.all([
      await axios.get(`/api/attendance/getMonthlySummary/${selectedMonth}`),
      await axios.get("/api/annualRequest/list-manager"),
    ]);
    console.log("✅ Shift data:", res.data.data);
    const presentCount = res.data.data.presentCount || 0;
    const lateCount = res.data.data.lateCount || 0;
    const request = leave.data.data || [];
    const requestCount = request.filter(
      (req) => req.status === "pending"
    ).length;

    const presentElement = document.getElementById("presentCount");
    const lateElement = document.getElementById("lateCount");
    const requestsCount = document.getElementById("requestCount");
    if (presentElement && lateElement) {
      presentElement.textContent = presentCount;
      lateElement.textContent = lateCount;
      requestsCount.textContent = requestCount;
    }
  } catch (error) {
    console.error("❌ Failed to fetch shift:", error);
    webix.message({ type: "error", text: "Failed to fetch shift data" });
  }
};

document.addEventListener("DOMContentLoaded", async () => {
  try {
    await fetchEmployees();
    renderEmployee();

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
      });
    }
  } catch (error) {
    console.error("❌ Unexpected error in DOMContentLoaded:", error);
    webix.message({ type: "error", text: "Failed to initialize page" });
  }
});
