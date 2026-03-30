// Select DOM elements
const form = document.getElementById("todo-form");
const input = document.getElementById("todo-input");
const list = document.getElementById("todo-list");
const filterButtons = document.querySelectorAll(".filters button");

// Load tasks from localStorage or initialize empty array
let todos = JSON.parse(localStorage.getItem("todos")) || [];

// Render tasks to the DOM
function render(filter = "all") {
  list.innerHTML = ""; // clear current list

  let filteredTodos = todos.filter(todo => {
    if(filter === "all") return true;
    if(filter === "active") return !todo.completed;
    if(filter === "completed") return todo.completed;
  });

  filteredTodos.forEach((todo, index) => {
    const li = document.createElement("li");
    li.dataset.index = index;
    li.className = todo.completed ? "completed" : "";
    li.innerHTML = `
      <span>${todo.text}</span>
      <div>
        <button class="complete-btn">${todo.completed ? "Undo" : "Complete"}</button>
        <button class="delete-btn">Delete</button>
      </div>
    `;
    list.appendChild(li);
  });
}

// Save tasks to localStorage
function save() {
  localStorage.setItem("todos", JSON.stringify(todos));
}

// Add a new task
form.addEventListener("submit", (e) => {
  e.preventDefault();
  const text = input.value.trim();
  if(text) {
    todos.push({ text, completed: false });
    input.value = "";
    save();
    render(currentFilter);
  }
});

// Event delegation for Complete and Delete buttons
list.addEventListener("click", (e) => {
  const li = e.target.closest("li");
  if(!li) return;
  const index = li.dataset.index;

  if(e.target.classList.contains("complete-btn")) {
    todos[index].completed = !todos[index].completed;
  }

  if(e.target.classList.contains("delete-btn")) {
    todos.splice(index, 1);
  }

  save();
  render(currentFilter);
});

// Filter tasks
let currentFilter = "all";
filterButtons.forEach(btn => {
  btn.addEventListener("click", () => {
    currentFilter = btn.dataset.filter;
    render(currentFilter);
  });
});

// Initial render
render();