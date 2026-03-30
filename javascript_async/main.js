import { fetchPosts, fetchUsers } from "./api.js";

const postsDiv = document.getElementById("posts");
const usersDiv = document.getElementById("users");
const statusDiv = document.getElementById("status");
const reloadBtn = document.getElementById("reload");

async function loadData() {
  try {
    statusDiv.textContent = "Loading...";

    const [posts, users] = await Promise.all([
      fetchPosts(),
      fetchUsers()
    ]);

    renderPosts(posts);
    renderUsers(users);

    statusDiv.textContent = "Loaded Successfully";
  } catch (err) {
    statusDiv.textContent = "Error: " + err.message;
  }
}

function renderPosts(posts) {
  postsDiv.innerHTML = "<h2>Posts</h2>";
  posts.slice(0, 5).forEach(p => {
    postsDiv.innerHTML += `<p>${p.title}</p>`;
  });
}

function renderUsers(users) {
  usersDiv.innerHTML = "<h2>Users</h2>";
  users.slice(0, 5).forEach(u => {
    usersDiv.innerHTML += `<p>${u.name}</p>`;
  });
}

reloadBtn.addEventListener("click", loadData);

// initial load
loadData();