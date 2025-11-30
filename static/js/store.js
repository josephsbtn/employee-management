// Load store data
const loadStores = async () => {
  try {
    const res = await axios.get("/api/branch");
    console.log("RES DATA BRANCH :", res.data);
    const storeTable = $$("storeTable");
    storeTable.clearAll();
    storeTable.parse(res.data);
  } catch (err) {
    console.error("Failed to load stores:", err);
    webix.alert("Failed to load store data!");
  }
};

const storeById = async (id) => {
  try {
    const res = await axios.get(`/api/branch/${id}`);
    return res.data;
  } catch (error) {
    webix.alert("Failed to load store data!");
  }
};
