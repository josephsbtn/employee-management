let schedule = [];
let currentShiftId = null;
let selectedMonth = null;
let isRequested = false;

const fetchSchedule = async () => {
  try {
    const user = await currentUser();
    console.log("user", user);
    console.log("LOADING GET SCHEDULE");
    const res = await axios.get(`/api/attendance/schedule/${user.id}`);
    console.log("RES DATA SCHEDULE :", res.data.data);
    schedule = res.data.data;
  } catch (error) {
    console.error("❌ Error fetching schedule:", error);
    webix.message({ type: "error", text: "Error fetching schedule." });
    return [];
  }
};

const renderSchedule = async (monthFilter) => {
  try {
    const scheduleList = document.getElementById("scheduleList");
    scheduleList.innerHTML = "";

    let selectedMonth =
      typeof monthFilter === "string"
        ? new Date(`${monthFilter}-01`)
        : monthFilter || new Date();

    console.log("data :", schedule);

    const filteredSchedule = schedule.filter((item) => {
      const date = new Date(item.Date);
      return (
        date.getMonth() === selectedMonth.getMonth() &&
        date.getFullYear() === selectedMonth.getFullYear()
      );
    });

    if (!filteredSchedule || filteredSchedule.length === 0) {
      scheduleList.innerHTML = `
    <div class="text-center text-gray-500 py-4">
      No schedule available for this month.
    </div>
  `;
      return;
    }

    const schedules = filteredSchedule.map((item) => {
      const date = new Date(item.Date).toLocaleDateString("en-US", {
        weekday: "short",
        year: "numeric",
        month: "short",
        day: "numeric",
      });

      let statusColor = "text-gray-500";
      if (item.status === "present")
        statusColor = "text-green-600 font-semibold";
      else if (item.status === "late")
        statusColor = "text-yellow-600 font-semibold";
      else if (item.status === "absent")
        statusColor = "text-red-600 font-semibold";

      return `
    <div class="bg-white p-4 rounded-xl border border-gray-100 shadow-sm hover:shadow-md transition">
      <div class="flex items-center justify-between mb-2">
        <h4 class="text-sm font-semibold text-gray-800">${date}</h4>
        <span class="px-2 py-1 rounded-md text-xs ${statusColor} bg-gray-50 border">${item.status}</span>
      </div>
      <p class="text-sm text-gray-600"><strong>Shift:</strong> ${item.shift}</p>
      <p class="text-sm text-gray-600"><strong>Start:</strong> ${item.shiftStartTime}</p>
      <p class="text-sm text-gray-600"><strong>End:</strong> ${item.shiftEndTime}</p>
    </div>
  `;
    });

    scheduleList.innerHTML = schedules.join("");
  } catch (error) {
    console.error("❌ Error rendering schedule:", error);
    webix.message({ type: "error", text: "Failed to load schedule." });
  }
};

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

    const currentPossition = await getCurrentLocation();
    console.log("currentPossition", currentPossition);
    const locationPayload = {
      type: "Point",
      coordinates: [currentPossition.longitude, currentPossition.latitude],
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
      await currentShift();
      console.log("Clock in successful!");
      isRequested = false;

      btn.classList.remove("opacity-50", "cursor-not-allowed");
      btn.disabled = false;
      return webix.message({ type: "success", text: "Clock in successful!" });
    }
    isRequested = false;
    btn.disabled = false;
    btn.classList.remove("opacity-50", "cursor-not-allowed");
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
      text: "Failed to clock in. Something went wrong ",
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
    const currentPossition = await getCurrentLocation();
    const locationPayload = {
      type: "Point",
      coordinates: [currentPossition.longitude, currentPossition.latitude],
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
      await currentShift();
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

const currentShift = async () => {
  try {
    const today = new Date().toLocaleDateString("en-US", {
      year: "numeric",
      month: "short",
      day: "numeric",
    });
    const myshift = schedule.filter((item) => {
      const date = new Date(item.Date).toLocaleDateString("en-US", {
        year: "numeric",
        month: "short",
        day: "numeric",
      });
      if (date === today) {
        currentShiftId = item._id;
        return item;
      }
    });
    const buttonContainer = document.getElementById("clockInOutContainer");
    const container = document.getElementById("currentShiftContainer");
    if (myshift.length === 0) {
      return (container.innerHTML = `
      <p
        class="text-xl font-semibold text-[var(--morning-blue)]"
        id="currentShift">
        Today is off
      </p>
    `);
    }
    console.log("myshift", myshift);
    const statusHtml =
      myshift[0].status === "present"
        ? `<p class="text-sm text-gray-500">You are present</p>`
        : myshift[0].status === "late"
        ? `<p class="text-sm text-gray-500">You are late</p>`
        : `<p class="text-sm text-gray-500">You are absent</p>`;

    container.innerHTML = `
    <p
      class="text-xl font-semibold text-[var(--morning-blue)]"
      id="currentShift">
      ${myshift[0].shift || "--"}
    </p>
    <p class="text-sm text-gray-500">${myshift[0].shiftStartTime || "--"} - ${
      myshift[0].shiftEndTime || "--"
    }</p>
  `;

    console.log("myshift clock in : ", myshift[0].clockIn);
    buttonContainer.innerHTML = ` 
    ${
      myshift[0].clockIn == null || myshift[0].clockIn === ""
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
    const clockInTime = document.getElementById("clockInTime");
    const clockOutTime = document.getElementById("clockOutTime");

    clockInTime.innerHTML = myshift[0].clockIn || "--";
    clockOutTime.innerHTML = myshift[0].clockOut || "--";
  } catch (error) {
    console.error("❌ Error getting current shift:", error);
    webix.message({ type: "error", text: "Failed to get current shift." });
  }
};

document.addEventListener("DOMContentLoaded", async () => {
  topNav();
  navbarSide();
  if (schedule.length === 0) {
    await fetchSchedule();
  }
  isRequested = false;

  const monthPicker = document.getElementById("monthPicker");
  if (monthPicker) {
    const now = new Date();
    const year = now.getFullYear();
    const month = String(now.getMonth() + 1).padStart(2, "0");
    const formattedMonth = `${year}-${month}`;

    monthPicker.value = formattedMonth;

    console.log("📅 Selected month:", formattedMonth);

    await renderSchedule(formattedMonth).then(async () => await currentShift());
    console.log("shift id", currentShiftId);

    monthPicker.addEventListener("change", async (e) => {
      await renderSchedule(e.target.value);
    });
  }
});
