const form = document.getElementById('studentForm');
const studentList = document.getElementById('studentList');

// Load students on page load
window.onload = loadStudents;

form.addEventListener('submit', async (e) => {
    e.preventDefault();

    const name = document.getElementById('name').value;
    const department = document.getElementById('department').value;
    const roll = document.getElementById('roll').value;

    await fetch('/add_student', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name, department, roll_number: roll })
    });

    form.reset();
    loadStudents();
});

async function loadStudents() {
    const res = await fetch('/get_students');
    const students = await res.json();

    studentList.innerHTML = '';

    students.forEach(student => {
        const li = document.createElement('li');
        li.textContent = `${student.name} | ${student.department} | ${student.roll_number}`;
        studentList.appendChild(li);
    });
}