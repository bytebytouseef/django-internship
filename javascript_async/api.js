export async function fetchPosts() {
  const res = await fetch("https://jsonplaceholder.typicode.com/posts");

  if (!res.ok) throw new Error("Posts fetch failed");

  return res.json();
}

export async function fetchUsers() {
  const res = await fetch("https://jsonplaceholder.typicode.com/users");

  if (!res.ok) throw new Error("Users fetch failed");

  return res.json();
}