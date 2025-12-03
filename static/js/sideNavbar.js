const pagesAdmin = [
  {
    href: "/dashboard",
    text: "Dashboard",
    icon: '<svg class="w-5 h-5 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1V10a1 1 0 00-1-1H7a1 1 0 00-1 1v10a1 1 0 001 1h2z"></path></svg>',
  },
  {
    href: "/owner/branch-manage",
    text: "Branch Store List",
    icon: '<svg class="w-5 h-5 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 10h16M4 14h16M4 18h16"></path></svg>',
  },
  {
    href: "/employee-manage",
    text: "Employee List",
    icon: '<svg class="w-5 h-5 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M15 21v-1a6 6 0 00-1.78-4.125a4 4 0 00-6.44 0A6 6 0 003 20v1h12z"></path></svg>',
  },
  {
    href: "/owner/leave-request",
    text: "Manage Leave Request",
    icon: `<svg class="w-5 h-5 mr-3" fill="none" stroke="currentColor" xmlns="http://www.w3.org/2000/svg" width="200" height="200" viewBox="0 0 2048 2048"><path fill="currentColor" d="M2048 1280v768H1024v-768h256v-256h512v256h256zm-640 0h256v-128h-256v128zm512 384h-128v128h-128v-128h-256v128h-128v-128h-128v256h768v-256zm0-256h-768v128h768v-128zm-355-512q-54-61-128-94t-157-34q-80 0-149 30t-122 82t-83 123t-30 149q0 92-41 173t-116 136q45 23 84 53t73 68v338q0-79-30-149t-82-122t-123-83t-149-30q-80 0-149 30t-122 82t-83 123t-30 149H0q0-73 20-141t57-129t90-108t118-81q-74-54-115-135t-42-174q0-79 30-149t82-122t122-83t150-30q92 0 173 41t136 116q38-75 97-134t135-98q-74-54-115-135t-42-174q0-79 30-149t82-122t122-83t150-30q79 0 149 30t122 82t83 123t30 149q0 92-41 173t-116 136q68 34 123 85t93 118h-158zM512 1408q53 0 99-20t82-55t55-81t20-100q0-53-20-99t-55-82t-81-55t-100-20q-53 0-99 20t-82 55t-55 81t-20 100q0 53 20 99t55 82t81 55t100 20zm512-1024q0 53 20 99t55 82t81 55t100 20q53 0 99-20t82-55t55-81t20-100q0-53-20-99t-55-82t-81-55t-100-20q-53 0-99 20t-82 55t-55 81t-20 100z"/></svg>`,
  },
  {
    href: "/owner/history",
    text: "History Log",
    icon: '<svg class="w-5 h-5 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01"></path></svg>',
  },
];

const pagesManager = [
  {
    href: "/dashboard",
    text: "Dashboard",
    icon: '<svg class="w-5 h-5 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1V10a1 1 0 00-1-1H7a1 1 0 00-1 1v10a1 1 0 001 1h2z"></path></svg>',
  },
  {
    href: "/employee-manage",
    text: "Employee List",
    icon: '<svg class="w-5 h-5 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M15 21v-1a6 6 0 00-1.78-4.125a4 4 0 00-6.44 0A6 6 0 003 20v1h12z"></path></svg>',
  },
  {
    href: "/manager/shift-schedule",
    text: "Shift Employees",
    icon: `<svg class="w-5 h-5 mr-3" fill="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><g id="SVGRepo_bgCarrier" stroke-width="0"></g><g id="SVGRepo_tracerCarrier" stroke-linecap="round" stroke-linejoin="round"></g><g id="SVGRepo_iconCarrier"><path d="M12,14a1,1,0,1,0-1-1A1,1,0,0,0,12,14Zm5,0a1,1,0,1,0-1-1A1,1,0,0,0,17,14Zm-5,4a1,1,0,1,0-1-1A1,1,0,0,0,12,18Zm5,0a1,1,0,1,0-1-1A1,1,0,0,0,17,18ZM7,14a1,1,0,1,0-1-1A1,1,0,0,0,7,14ZM19,4H18V3a1,1,0,0,0-2,0V4H8V3A1,1,0,0,0,6,3V4H5A3,3,0,0,0,2,7V19a3,3,0,0,0,3,3H19a3,3,0,0,0,3-3V7A3,3,0,0,0,19,4Zm1,15a1,1,0,0,1-1,1H5a1,1,0,0,1-1-1V10H20ZM20,8H4V7A1,1,0,0,1,5,6H19a1,1,0,0,1,1,1ZM7,18a1,1,0,1,0-1-1A1,1,0,0,0,7,18Z"></path></g></svg>`,
  },
  {
    href: "/employees/leave-request",
    text: "Leave Request",
    icon: `<svg class="w-5 h-5 mr-3" xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 2048 2048" fill="currentColor" stroke="currentColor"><path fill="currentColor" d="M1536 1024q106 0 199 40t163 109t110 163t40 200q0 106-40 199t-109 163t-163 110t-200 40q-106 0-199-40t-163-109t-110-163t-40-200q0-106 40-199t109-163t163-110t200-40zm0 896q79 0 149-30t122-82t83-122t30-150q0-79-30-149t-82-122t-123-83t-149-30q-80 0-149 30t-122 82t-83 123t-30 149q0 80 30 149t82 122t122 83t150 30zm0-384h192v128h-320v-384h128v256zm-366-524q-28 20-53 42t-48 47q-69-37-145-57t-156-20q-88 0-170 23t-153 64t-129 100t-100 130t-65 153t-23 170H0q0-120 35-231t101-205t156-167t204-115q-113-74-176-186t-64-248q0-106 40-199t109-163T568 40T768 0q106 0 199 40t163 109t110 163t40 200q0 66-16 129t-48 119t-76 104t-101 82q70 28 131 66zM384 512q0 80 30 149t82 122t122 83t150 30q79 0 149-30t122-82t83-122t30-150q0-79-30-149t-82-122t-123-83t-149-30q-80 0-149 30t-122 82t-83 123t-30 149z"/></svg>`,
  },
  {
    href: "/manager/leave-request",
    text: "Manage Leave Request",
    icon: `<svg class="w-5 h-5 mr-3" fill="none" stroke="currentColor" xmlns="http://www.w3.org/2000/svg" width="200" height="200" viewBox="0 0 2048 2048"><path fill="currentColor" d="M2048 1280v768H1024v-768h256v-256h512v256h256zm-640 0h256v-128h-256v128zm512 384h-128v128h-128v-128h-256v128h-128v-128h-128v256h768v-256zm0-256h-768v128h768v-128zm-355-512q-54-61-128-94t-157-34q-80 0-149 30t-122 82t-83 123t-30 149q0 92-41 173t-116 136q45 23 84 53t73 68v338q0-79-30-149t-82-122t-123-83t-149-30q-80 0-149 30t-122 82t-83 123t-30 149H0q0-73 20-141t57-129t90-108t118-81q-74-54-115-135t-42-174q0-79 30-149t82-122t122-83t150-30q92 0 173 41t136 116q38-75 97-134t135-98q-74-54-115-135t-42-174q0-79 30-149t82-122t122-83t150-30q79 0 149 30t122 82t83 123t30 149q0 92-41 173t-116 136q68 34 123 85t93 118h-158zM512 1408q53 0 99-20t82-55t55-81t20-100q0-53-20-99t-55-82t-81-55t-100-20q-53 0-99 20t-82 55t-55 81t-20 100q0 53 20 99t55 82t81 55t100 20zm512-1024q0 53 20 99t55 82t81 55t100 20q53 0 99-20t82-55t55-81t20-100q0-53-20-99t-55-82t-81-55t-100-20q-53 0-99 20t-82 55t-55 81t-20 100z"/></svg>`,
  },
  {
    href: "/manager/history",
    text: "History",
    icon: `<svg class="w-5 h-5 mr-3"
     xmlns="http://www.w3.org/2000/svg"
     width="24"
     height="24"
     viewBox="0 0 24 24"
     fill="currentColor"
     stroke="currentColor">
  <g transform="scale(0.0234375)">
    <path d="M320.9 704v-32l131-177q5-20 22-33.5t39-13.5q21 0 38 12.5t23 32.5l195 243v32h-32l-225-181l-159 117h-32zm192 320q-104 0-197.5-39.5T150.9 874l91-90q53 53 123 82.5t148 29.5q104 0 192.5-51.5t140-140T896.9 512t-51.5-192.5t-140-140T512.9 128q-94 0-175 43t-135 116l54 54q0 18-12.5 30.5T214.9 384h-171q-18 0-30.5-12.5T.9 341V171q0-17 12.5-29.5T43.9 129l68 67q71-91 176-143.5T512.9 0q104 0 199 40.5t163.5 109t109 163.5t40.5 199t-40.5 199t-109 163.5t-163.5 109t-199 40.5z"/>
  </g>
</svg>
`,
  },
];

const pagesEmployee = [
  {
    href: "/dashboard",
    text: "Dashboard",
    icon: '<svg class="w-5 h-5 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1V10a1 1 0 00-1-1H7a1 1 0 00-1 1v10a1 1 0 001 1h2z"></path></svg>',
  },
  {
    href: "/employees/leave-request",
    text: "Annual Leave Request",
    icon: `<svg class="w-5 h-5 mr-3" xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 2048 2048" fill="currentColor" stroke="currentColor"><path fill="currentColor" d="M1536 1024q106 0 199 40t163 109t110 163t40 200q0 106-40 199t-109 163t-163 110t-200 40q-106 0-199-40t-163-109t-110-163t-40-200q0-106 40-199t109-163t163-110t200-40zm0 896q79 0 149-30t122-82t83-122t30-150q0-79-30-149t-82-122t-123-83t-149-30q-80 0-149 30t-122 82t-83 123t-30 149q0 80 30 149t82 122t122 83t150 30zm0-384h192v128h-320v-384h128v256zm-366-524q-28 20-53 42t-48 47q-69-37-145-57t-156-20q-88 0-170 23t-153 64t-129 100t-100 130t-65 153t-23 170H0q0-120 35-231t101-205t156-167t204-115q-113-74-176-186t-64-248q0-106 40-199t109-163T568 40T768 0q106 0 199 40t163 109t110 163t40 200q0 66-16 129t-48 119t-76 104t-101 82q70 28 131 66zM384 512q0 80 30 149t82 122t122 83t150 30q79 0 149-30t122-82t83-122t30-150q0-79-30-149t-82-122t-123-83t-149-30q-80 0-149 30t-122 82t-83 123t-30 149z"/></svg>`,
  },
  {
    href: "/employees/history",
    text: "History",
    icon: `<svg class="w-5 h-5 mr-3"
     xmlns="http://www.w3.org/2000/svg"
     width="24"
     height="24"
     viewBox="0 0 24 24"
     fill="currentColor"
     stroke="currentColor">
  <g transform="scale(0.0234375)">
    <path d="M320.9 704v-32l131-177q5-20 22-33.5t39-13.5q21 0 38 12.5t23 32.5l195 243v32h-32l-225-181l-159 117h-32zm192 320q-104 0-197.5-39.5T150.9 874l91-90q53 53 123 82.5t148 29.5q104 0 192.5-51.5t140-140T896.9 512t-51.5-192.5t-140-140T512.9 128q-94 0-175 43t-135 116l54 54q0 18-12.5 30.5T214.9 384h-171q-18 0-30.5-12.5T.9 341V171q0-17 12.5-29.5T43.9 129l68 67q71-91 176-143.5T512.9 0q104 0 199 40.5t163.5 109t109 163.5t40.5 199t-40.5 199t-109 163.5t-163.5 109t-199 40.5z"/>
  </g>
</svg>
`,
  },
];

const listRole = async () => {
  const user = await currentUser();
  if (user.role === "owner") {
    return [
      { id: "employee", value: "Employee" },
      { id: "manager", value: "Manager" },
    ];
  }
  if (user.role === "manager") {
    return [{ id: "employee", value: "Employee" }];
  }
};

const currentUser = async () => {
  try {
    const nameText = document.getElementById("current-user-name") || "";
    const res = await fetch("/auth/current", { method: "GET" });
    const data = await res.json();
    if (nameText) nameText.textContent = data.name;
    return {
      id: data._id,
      name: data.name,
      role: data.role,
    };
  } catch (error) {
    webix.message({ type: "error", text: "Error fetching user data" });
  }
};
function escapeHTML(str) {
  return str
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}

const greetings = [
  `Hey <span class="text-[var(--sunrise-red)]">{name}</span>, welcome back!`,
  `Good to see you, <span class="text-[var(--sunrise-red)]">{name}</span>!`,
  `Morning vibes, <span class="text-[var(--sunrise-red)]">{name}</span>!`,
  `Glad you’re here, <span class="text-[var(--sunrise-red)]">{name}</span>!`,
  `Let’s do this, <span class="text-[var(--sunrise-red)]">{name}</span>!`,
  `You got this, <span class="text-[var(--sunrise-red)]">{name}</span>!`,
  `Nice to see you, <span class="text-[var(--sunrise-red)]">{name}</span>!`,
  `Happy to see you, <span class="text-[var(--sunrise-red)]">{name}</span>!`,
  `Ready to roll, <span class="text-[var(--sunrise-red)]">{name}</span>?`,
  `All set, <span class="text-[var(--sunrise-red)]">{name}</span>?`,
  `Let’s go, <span class="text-[var(--sunrise-red)]">{name}</span>!`,
  `Welcome home, <span class="text-[var(--sunrise-red)]">{name}</span>!`,
  `Good day, <span class="text-[var(--sunrise-red)]">{name}</span>!`,
  `How’s it going, <span class="text-[var(--sunrise-red)]">{name}</span>?`,
  `Stay awesome, <span class="text-[var(--sunrise-red)]">{name}</span>!`,
];

function getRandomGreeting(name) {
  const firstName = name.split(" ")[0];
  const random = greetings[Math.floor(Math.random() * greetings.length)];
  return random.replace("{name}", firstName);
}

const topNav = async () => {
  console.log("topNav");
  const topNavContainer = document.getElementById("top-nav");
  if (!topNavContainer) return;

  const user = await currentUser();
  const greetingHTML = getRandomGreeting(user.name);

  topNavContainer.innerHTML = `
    <div class="flex items-center justify-between w-full">
      <div class="flex items-center space-x-2">
        <h1 class="text-xl font-semibold text-[var(--text-primary)]">
          ${greetingHTML}
        </h1>
      </div>
      
      <div class="flex items-center space-x-4">
        <div class="relative" id="userDropdown">
          <button class="flex items-center space-x-2 p-2 rounded-lg hover:bg-gray-100 transition-colors duration-200" id="userMenuButton" aria-expanded="false" aria-haspopup="true">
            <div class="w-8 h-8 rounded-full bg-[var(--sunrise-red)] shadow-md flex items-center justify-center text-white font-semibold">
              ${user.name.charAt(0).toUpperCase()}
            </div>
            <span class="hidden md:block text-sm font-medium text-[var(--text-primary)]">${
              user.name
            }</span>
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="text-[var(--text-secondary)]">
              <polyline points="6 9 12 15 18 9"></polyline>
            </svg>
          </button>
          
          <div class="absolute right-0 mt-2 w-48 bg-white rounded-lg shadow-lg py-1 z-10 hidden" id="userDropdownMenu">
            <a href="/profile" class="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 transition-colors duration-150">Profile</a>
            <hr class="my-1">
            <a href="#" onclick="logout()" id="logoutLink" class="block px-4 py-2 text-sm text-red-600 hover:bg-gray-100 transition-colors duration-150 flex items-center space-x-2">
              <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"></path>
                <polyline points="16 17 21 12 16 7"></polyline>
                <line x1="21" y1="12" x2="9" y2="12"></line>
              </svg>
              <span>Logout</span>
            </a>
          </div>
        </div>
      </div>
    </div>
  `;

  const userMenuButton = document.getElementById("userMenuButton");
  const userDropdownMenu = document.getElementById("userDropdownMenu");

  if (userMenuButton && userDropdownMenu) {
    userMenuButton.addEventListener("click", () => {
      const isExpanded =
        userMenuButton.getAttribute("aria-expanded") === "true";
      userMenuButton.setAttribute("aria-expanded", !isExpanded);
      userDropdownMenu.classList.toggle("hidden");
    });

    document.addEventListener("click", (event) => {
      if (!document.getElementById("userDropdown").contains(event.target)) {
        userDropdownMenu.classList.add("hidden");
        userMenuButton.setAttribute("aria-expanded", "false");
      }
    });
  }

  const logoutLink = document.getElementById("logoutLink");
  if (logoutLink) {
    logoutLink.addEventListener("click", (e) => {
      e.preventDefault();
    });
  }
};

const navbarSide = async () => {
  user = await currentUser();
  pages =
    user.role === "owner"
      ? pagesAdmin
      : user.role === "manager"
      ? pagesManager
      : pagesEmployee;
  const navbarContainer = document.getElementById("sidebar-container");
  const currentPageTitle = document.getElementById("currentPage")
    ? document.getElementById("currentPage")
    : "";

  if (!navbarContainer) return;

  const currentPath = window.location.pathname;

  const activePage = pages.find((item) => item.href === currentPath);

  if (activePage) {
    currentPageTitle.innerHTML = activePage.text;
  } else {
    currentPageTitle.innerHTML = "Dashboard";
  }

  const linksHTML = pages
    .map((item) => {
      const isActive =
        currentPath === item.href
          ? "bg-[var(--sunrise-red)] text-[var(--pure-white)] shadow-md"
          : "text-[var(--arunika-currentColor)] text-opacity-80 bg-[var(--pure-white)] hover:bg-gray-100 bg-opacity-10 hover:bg-opacity-20 hover:shadow-md hover:shadow-[var(--sunrise-red)]/50 hover:text-[var(--text-secondary)]";

      return `
            <a href="${
              item.href
            }" class="text-xs flex items-center gap-4 text-base transition-all duration-300 px-4 py-2.5 rounded-xl ${isActive}">
                ${item.icon || ""}
                <span class="text-xs">${item.text}</span>
            </a>
        `;
    })
    .join("");

  navbarContainer.innerHTML = `
        <div class="flex flex-col justify-between h-full">
            <div>
                <div class="flex items-center justify-center py-4">
                    <h1 class="text-3xl font-bold text-[var(--sunrise-red)]">Aventra</h1>
                </div>
                <div class="flex flex-col gap-2 border-t-[1px] border-[#e7e7e7] py-6 px-4">
                    <p class="text-xs font-semibold text-gray-500 uppercase tracking-wider px-4 mb-2">Navigation</p>
                    ${linksHTML}
                </div>
            </div>
            <div class="flex text-xs text-center flex-col gap-2 border-t-[1px] border-[#e7e7e7] py-6">
              Aventra Inc. 2023
            </div>
             
        </div>
    `;
};

const logout = async () => {
  webix.message("Logging out...");
  try {
    const response = await axios.post("/auth/logout", {
      headers: { "Content-Type": "application/json" },
    });
    if (!response.data.status) throw new Error("Logout failed");

    setTimeout(() => {
      webix.message({
        type: "success",
        text: "Logged out successfully!",
      });
      window.location.href = "/";
    }, 500);
  } catch (error) {
    console.error(error);
    webix.message({ type: "error", text: "Error logging out" });
  }
};
