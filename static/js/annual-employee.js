const closeDetail = () => {
  const container = document.getElementById("detailRequest");
  if (container) {
    container.classList.add("hidden");
  }
};

const formatDate = (data) => {
  const date = new Date(data);
  const day = date.getDate();
  const month = date.toLocaleString("en-GB", { month: "short" });
  const year = date.getFullYear();
  return `${day} ${month} ${year}`;
};

const renderDetail = async (id) => {
  try {
    const detail = await axios.get(`/api/annualRequest/detail/${id}`);
    const data = detail.data.data;

    console.log("data", data);
    const container = document.getElementById("detailRequest");
    container.classList.remove("hidden");
    if (container) {
      const statusClass =
        data.status === "approved"
          ? "bg-green-100 text-green-700 px-2 py-1 rounded"
          : data.status === "pending"
          ? "bg-yellow-100 text-yellow-700 px-2 py-1 rounded"
          : data.status === "rejected"
          ? "bg-red-100 text-red-700 px-2 py-1 rounded"
          : "bg-gray-100 text-gray-700 px-2 py-1 rounded";

      const typeClass =
        data.type === "annual"
          ? "bg-blue-100 text-blue-700 px-2 py-1 rounded"
          : data.type === "sick"
          ? "bg-orange-100 text-orange-700 px-2 py-1 rounded"
          : data.type === "permission"
          ? "bg-sky-100 text-sky-700 px-2 py-1 rounded"
          : data.type === "unpaid"
          ? "bg-gray-200 text-gray-700 px-2 py-1 rounded"
          : "bg-gray-100 text-gray-700 px-2 py-1 rounded";

      const formatted = data.type.charAt(0).toUpperCase() + data.type.slice(1);
      const status = data.status.charAt(0).toUpperCase() + data.status.slice(1);
      const start = formatDate(data.startDate);
      const end = formatDate(data.endDate);

      container.innerHTML = `
  <div class="w-[800px] h-fit rounded-lg bg-white shadow-md flex flex-col gap-4">
    
    <div class="flex items-center w-full justify-between p-4 border-b border-[var(--warm-gray)]">
      <div class="flex flex-col items-start gap-2">
        <h1 class="text-xl font-semibold text-[var(--text-primary)]">Leave Request</h1>
        <h2 class="text-xs text-[var(--text-secondary)]">Request ID: ${
          data._id
        }</h2>
      </div>
      <button onclick="closeDetail()" class="px-4 py-2 rounded-lg text-sm font-medium text-[var(--text-secondary)] hover:text-white hover:bg-[var(--sunrise-red)] transition duration-150">
       <span class="font-bold text-lg">X</span>
      </button>
    </div>

    <div class="flex items-start w-full justify-between px-4">
      <div class="flex flex-col w-[55%] items-center justify-center px-4 py-2 border-r border-[var(--warm-gray)]">
        <div class="flex justify-between w-full gap-4">
          <h1 class="text-lg font-semibold text-[var(--text-primary)] my-1 ${typeClass}">
            ${formatted} Leave Request
          </h1> 
          <p class="text-xs font-semibold ${statusClass} flex items-center justify-center">
            ${status}
          </p>
        </div>

        <p class="text-xs text-[var(--text-secondary)] text-left w-full">
          ${start} - ${end} (${data.days} days)
        </p>

        <div class="flex w-full p-2 border border-[var(--warm-gray)] rounded-lg my-4">
          <div class="w-8 h-8 rounded-full bg-[var(--sunrise-red)] shadow-md flex items-center justify-center text-white font-semibold">
            ${data.employee.name.charAt(0).toUpperCase()}
          </div>
          <div class="flex flex-col items-start ml-4">
            <h1 class="text-sm font-semibold text-[var(--text-primary)]">
              ${data.employee.name}
            </h1>
            <p class="text-xs text-[var(--text-secondary)]">
              ${data.employee.email}
            </p>
          </div>
        </div>

        <div class="flex flex-col w-full items-start justify-center">
          <h1 class="text-lg font-semibold text-[var(--text-primary)]">Reason</h1>
          <p class="text-sm text-[var(--text-secondary)] p-2 border border-[var(--warm-gray)] rounded-lg min-w-full">
            ${data.reason}
          </p>
        </div>

        <div class="flex flex-col w-full items-start justify-center my-4">
          ${
            data.fileName
              ? renderAttachment(data.fileName, data.attachmentUrl)
              : '<p class="text-sm text-[var(--text-secondary)]">No attachment</p>'
          }
        </div>
      </div>

      <div class="flex flex-col w-[45%] items-start justify-start px-4 py-2">
        <div class="flex flex-col w-full items-start justify-start mb-4">
          <h1 class="text-lg font-semibold text-[var(--text-primary)] mb-2">Review</h1>
          
          ${
            data.reviewer
              ? `
            <div class="flex w-full p-2 border border-[var(--warm-gray)] rounded-lg mb-3">
              <div class="w-8 h-8 rounded-full bg-[var(--calm-blue)] shadow-md flex items-center justify-center text-white font-semibold text-xs">
                ${data.reviewer.name.charAt(0).toUpperCase()}
              </div>
              <div class="flex flex-col items-start ml-3">
                <h1 class="text-sm font-semibold text-[var(--text-primary)]">
                  ${data.reviewer.name}
                </h1>
                <p class="text-xs text-[var(--text-secondary)]">
                  Reviewer
                </p>
              </div>
            </div>
          `
              : ""
          }
          
          <p class="text-sm text-[var(--text-secondary)] p-2 border border-[var(--warm-gray)] rounded-lg min-w-full mb-2">
            ${data?.reviewer?.note || "No review comment yet"}
          </p>
          
          ${
            data.reviewer
              ? `
            <div class="flex items-center gap-2 text-xs text-[var(--text-secondary)] mt-1">
              <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-4 h-4">
                <path stroke-linecap="round" stroke-linejoin="round" d="M12 6v6h4.5m4.5 0a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <span>Reviewed on ${new Date(data.createdAt + "Z").toLocaleString(
                "id-ID",
                {
                  year: "numeric",
                  month: "long",
                  day: "numeric",
                  hour: "2-digit",
                  minute: "2-digit",
                }
              )}</span>
            </div>
          `
              : `
            <div class="flex items-center gap-2 text-xs text-yellow-600 mt-1">
              <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-4 h-4">
                <path stroke-linecap="round" stroke-linejoin="round" d="M12 6v6h4.5m4.5 0a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <span>Pending review</span>
            </div>
          `
          }
        </div>

        <div class="flex flex-col w-full items-start justify-start pt-4 border-t border-[var(--warm-gray)]">
          <h1 class="text-sm font-semibold text-[var(--text-primary)] mb-2">Request Information</h1>
          <div class="flex items-start gap-2 text-xs text-[var(--text-secondary)]">
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-4 h-4 mt-0.5">
              <path stroke-linecap="round" stroke-linejoin="round" d="M6.75 3v2.25M17.25 3v2.25M3 18.75V7.5a2.25 2.25 0 012.25-2.25h13.5A2.25 2.25 0 0121 7.5v11.25m-18 0A2.25 2.25 0 005.25 21h13.5A2.25 2.25 0 0021 18.75m-18 0v-7.5A2.25 2.25 0 015.25 9h13.5A2.25 2.25 0 0121 11.25v7.5" />
            </svg>
            <div class="flex flex-col">
              <span class="font-medium text-[var(--text-primary)]">Submitted on</span>
              <span>${new Date(data.createdAt + "Z").toLocaleString("id-ID", {
                year: "numeric",
                month: "long",
                day: "numeric",
                hour: "2-digit",
                minute: "2-digit",
              })}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
`;
    }
  } catch (error) {
    console.error(error);
  }
};

const renderDetailManager = async (id) => {
  try {
    const detail = await axios.get(`/api/annualRequest/detail/${id}`);
    const data = detail.data.data;

    console.log("data", data);
    const container = document.getElementById("detailRequest");
    container.classList.remove("hidden");

    if (container) {
      const statusClass =
        data.status === "approved"
          ? "bg-green-100 text-green-700 px-2 py-1 rounded"
          : data.status === "pending"
          ? "bg-yellow-100 text-yellow-700 px-2 py-1 rounded"
          : data.status === "rejected"
          ? "bg-red-100 text-red-700 px-2 py-1 rounded"
          : "bg-gray-100 text-gray-700 px-2 py-1 rounded";

      const typeClass =
        data.type === "annual"
          ? "bg-blue-100 text-blue-700 px-2 py-1 rounded"
          : data.type === "sick"
          ? "bg-orange-100 text-orange-700 px-2 py-1 rounded"
          : data.type === "permission"
          ? "bg-sky-100 text-sky-700 px-2 py-1 rounded"
          : data.type === "unpaid"
          ? "bg-gray-200 text-gray-700 px-2 py-1 rounded"
          : "bg-gray-100 text-gray-700 px-2 py-1 rounded";

      const formatted = data.type.charAt(0).toUpperCase() + data.type.slice(1);
      const status = data.status.charAt(0).toUpperCase() + data.status.slice(1);
      const start = formatDate(data.startDate);
      const end = formatDate(data.endDate);

      container.innerHTML = `
        <div class="w-[900px] h-fit rounded-lg bg-white shadow-md flex flex-col gap-4">
          
          <div class="flex items-center w-full justify-between p-4 border-b border-[var(--warm-gray)]">
            <div class="flex flex-col items-start gap-2">
              <h1 class="text-xl font-semibold text-[var(--text-primary)]">Leave Request</h1>
              <h2 class="text-xs text-[var(--text-secondary)]">Request ID: ${
                data._id
              }</h2>
            </div>
            <button onclick="closeDetail()" class="px-4 py-2 rounded-lg text-sm font-medium text-[var(--text-secondary)] hover:text-white hover:bg-[var(--sunrise-red)] transition duration-150">
              <span class="font-bold text-lg">X</span>
            </button>
          </div>

          <div class="flex items-start w-full justify-between px-4">
            <div class="flex flex-col w-[50%] items-center justify-center px-4 py-2 border-r border-[var(--warm-gray)]">
              <div class="flex justify-between w-full gap-4">
                <h1 class="text-lg font-semibold text-[var(--text-primary)] my-1 ${typeClass}">
                  ${formatted} Leave Request
                </h1> 
                <p class="text-xs font-semibold ${statusClass} flex items-center justify-center">
                  ${status}
                </p>
              </div>

              <p class="text-xs text-[var(--text-secondary)] text-left w-full">
                ${start} - ${end} (${data.days} days)
              </p>

              <div class="flex w-full p-2 border border-[var(--warm-gray)] rounded-lg my-4">
                <div class="w-8 h-8 rounded-full bg-[var(--sunrise-red)] shadow-md flex items-center justify-center text-white font-semibold">
                  ${data.employee.name.charAt(0).toUpperCase()}
                </div>
                <div class="flex flex-col items-start ml-4">
                  <h1 class="text-sm font-semibold text-[var(--text-primary)]">
                    ${data.employee.name}
                  </h1>
                  <p class="text-xs text-[var(--text-secondary)]">
                    ${data.employee.email}
                  </p>
                </div>
              </div>

              <div class="flex flex-col w-full items-start justify-center">
                <h1 class="text-lg font-semibold text-[var(--text-primary)]">Reason</h1>
                <p class="text-sm text-[var(--text-secondary)] p-2 border border-[var(--warm-gray)] rounded-lg min-w-full">
                  ${data.reason}
                </p>
              </div>

              <div class="flex flex-col w-full items-start justify-center my-4">
                ${
                  data.fileName
                    ? renderAttachment(data.fileName, data.attachmentUrl)
                    : '<p class="text-sm text-[var(--text-secondary)]">No attachment</p>'
                }
              </div>
            </div>

            <div class="flex flex-col w-[50%] items-start justify-start px-4 py-2">
              <div class="flex flex-col w-full items-start justify-start mb-4">
                ${
                  data.status === "pending"
                    ? `
                <div class="flex flex-col w-full items-start justify-start">
                  <h1 class="text-lg font-semibold text-[var(--text-primary)] mb-2">Add Review Comment</h1>
                  <textarea 
                    id="reviewComment" 
                    class="w-full p-2 border border-[var(--warm-gray)] rounded-lg text-sm resize-none" 
                    rows="3" 
                    placeholder="Add your comment here (optional for approve, required for reject)..."
                  ></textarea>
                  
                  <div class="flex gap-3 w-full mt-4">
                    <button 
                      onclick="handleApprove('${data._id}')" 
                      class="flex-1 bg-green-500 hover:bg-green-600 text-white px-4 py-2 rounded-lg text-sm font-medium transition duration-150"
                    >
                      ✓ Approve
                    </button>
                    <button 
                      onclick="handleReject('${data._id}')" 
                      class="flex-1 bg-red-500 hover:bg-red-600 text-white px-4 py-2 rounded-lg text-sm font-medium transition duration-150"
                    >
                      ✗ Reject
                    </button>
                  </div>
                </div>
                `
                    : `
                <div class="flex flex-col w-full items-start justify-start">
                  <h1 class="text-lg font-semibold text-[var(--text-primary)] mb-2">Review</h1>
                  
                  ${
                    data.reviewer
                      ? `
                  <div class="flex w-full p-2 border border-[var(--warm-gray)] rounded-lg mb-3">
                    <div class="w-8 h-8 rounded-full bg-[var(--calm-blue)] shadow-md flex items-center justify-center text-white font-semibold text-xs">
                      ${data.reviewer.name.charAt(0).toUpperCase()}
                    </div>
                    <div class="flex flex-col items-start ml-3">
                      <h1 class="text-sm font-semibold text-[var(--text-primary)]">
                        ${data.reviewer.name}
                      </h1>
                      <p class="text-xs text-[var(--text-secondary)]">
                        Reviewer
                      </p>
                    </div>
                  </div>
                  `
                      : ""
                  }
                  <p class="text-sm text-[var(--text-primary)] p-2 border border-[var(--warm-gray)] rounded-lg min-w-full mb-2">
                    ${data.reviewer.note || "No review comment"}
                  </p>
                  
                  ${
                    data.reviewer
                      ? `
                  <div class="flex items-center gap-2 text-xs text-[var(--text-secondary)] mt-1">
                    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-4 h-4">
                      <path stroke-linecap="round" stroke-linejoin="round" d="M12 6v6h4.5m4.5 0a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                    <span>Reviewed on ${new Date(
                      data.createdAt + "Z"
                    ).toLocaleString("id-ID", {
                      year: "numeric",
                      month: "long",
                      day: "numeric",
                      hour: "2-digit",
                      minute: "2-digit",
                    })}</span>
                  </div>
                  `
                      : ""
                  }
                </div>
                `
                }
              </div>

              <div class="flex flex-col w-full items-start justify-start pt-4 border-t border-[var(--warm-gray)] mt-4">
                <h1 class="text-sm font-semibold text-[var(--text-primary)] mb-2">Request Information</h1>
                <div class="flex items-start gap-2 text-xs text-[var(--text-secondary)]">
                  <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-4 h-4 mt-0.5">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M6.75 3v2.25M17.25 3v2.25M3 18.75V7.5a2.25 2.25 0 012.25-2.25h13.5A2.25 2.25 0 0121 7.5v11.25m-18 0A2.25 2.25 0 005.25 21h13.5A2.25 2.25 0 0021 18.75m-18 0v-7.5A2.25 2.25 0 015.25 9h13.5A2.25 2.25 0 0121 11.25v7.5" />
                  </svg>
                  <div class="flex flex-col">
                    <span class="font-medium text-[var(--text-primary)]">Submitted on</span>
                    <span>${new Date(data.createdAt + "Z").toLocaleString(
                      "id-ID",
                      {
                        year: "numeric",
                        month: "long",
                        day: "numeric",
                        hour: "2-digit",
                        minute: "2-digit",
                      }
                    )}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      `;
    }
  } catch (error) {
    console.error(error);
    webix.message({ type: "error", text: "Failed to fetch request details" });
  }
};

const renderAttachment = (fileName, fileUrl) => {
  return `
    <div class="flex flex-col">
      <p class="text-lg font-semibold text-[var(--text-primary)]">Attachment</p>
      <div class="flex items-center justify-between border rounded-lg p-3 bg-white shadow-sm gap-2">
        <div class="flex items-center gap-3">
          <div class="w-8 h-8 bg-blue-100 text-blue-600 rounded flex items-center justify-center">
            <svg class="w-6 h-6" xmlns="http://www.w3.org/2000/svg" width="200" height="200" viewBox="0 0 20 20" fill="currentColor"><g fill="currentColor" fill-rule="evenodd" clip-rule="evenodd"><path d="M5.75 11.5a.75.75 0 0 1 .75-.75h7a.75.75 0 0 1 0 1.5h-7a.75.75 0 0 1-.75-.75Zm0 3a.75.75 0 0 1 .75-.75h7a.75.75 0 0 1 0 1.5h-7a.75.75 0 0 1-.75-.75Z"/><path d="M2.5 2.5c0-1.102.898-2 2-2h6.69c.562 0 1.092.238 1.465.631l.006.007l4.312 4.702c.359.383.527.884.527 1.36v10.3c0 1.102-.898 2-2 2h-11c-1.102 0-2-.898-2-2v-15Zm8.689 0H4.5v15h11V7.192l-4.296-4.685l-.003-.001a.041.041 0 0 0-.012-.006Z"/><path d="M11.19.5a1 1 0 0 1 1 1v4.7h4.31a1 1 0 1 1 0 2h-5.31a1 1 0 0 1-1-1V1.5a1 1 0 0 1 1-1Z"/></g></svg>
          </div>
          <span class="text-sm text-[var(--text-primary)] max-w-[200px] truncate px-2">
            ${fileName}
          </span>
        </div>
        <a 
          href="${fileUrl}" 
          target="_blank"
          class="text-sm font-medium text-blue-600 hover:underline px-2 py-1 rounded-lg border border-blue-600 hover:bg-blue-600 hover:text-white transition duration-150"
        >
          Open
        </a>
      </div>
    </div>
  `;
};

const handleApprove = (id) => {
  const comment = document.getElementById("reviewComment").value.trim() || "";

  webix.confirm({
    title: "Approve Request",
    text: "Are you sure you want to approve this request?",
    ok: "Yes, Approve",
    cancel: "Cancel",
    callback: async (result) => {
      if (result && id) {
        await approveHandler(id, comment);
      }
    },
  });
};

const handleReject = (id) => {
  const comment = document.getElementById("reviewComment").value.trim() || "";

  if (!comment) {
    webix.message({
      type: "error",
      text: "Please provide a reason for rejection",
    });
    return;
  }

  webix.confirm({
    title: "Reject Request",
    text: "Are you sure you want to reject this request?",
    ok: "Yes, Reject",
    cancel: "Cancel",
    callback: async (result) => {
      if (result && id) {
        await rejectHandler(id, comment);
      }
    },
  });
};

const approveHandler = async (id, comment) => {
  try {
    webix.message("loading...");
    const response = await axios.put(`/api/annualRequest/approve/${id}`, {
      note: comment,
    });

    if (response.status === 200) {
      webix.message({
        type: "success",
        text: "Request approved successfully!",
      });
      await fetchListRequest();
      closeDetail();
      return {
        type: "success",
        text: "Request approved successfully!",
      };
    }
  } catch (error) {
    console.error("❌ Failed to approve request:", error);
    webix.message({
      type: "error",
      text: error.response?.data?.message || "Failed to approve request",
    });
    return {
      type: "error",
      text: error.response?.data?.message || "Failed to approve request",
    };
  }
};

const rejectHandler = async (id, comment) => {
  console.log("COMMENT : ", comment);
  try {
    webix.message("loading...");
    const response = await axios.put(`/api/annualRequest/reject/${id}`, {
      note: comment,
    });

    if (response.status === 200) {
      webix.message({
        type: "success",
        text: "Request rejected successfully!",
      });
      await fetchListRequest();
      closeDetail();
      return {
        type: "success",
        text: "Request rejected successfully!",
      };
    }
  } catch (error) {
    console.error("❌ Failed to reject request:", error);
    webix.message({
      type: "error",
      text: error.response?.data?.message || "Failed to reject request",
    });
    return {
      type: "error",
      text: error.response?.data?.message || "Failed to reject request",
    };
  }
};
