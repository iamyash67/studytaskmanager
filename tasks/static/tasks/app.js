function getCookie(name) {
  const value = `; ${document.cookie}`;
  const parts = value.split(`; ${name}=`);
  if (parts.length === 2) return parts.pop().split(';').shift();
  return null;
}

function setStatus(message, type = "success") {
  const box = document.getElementById("status-msg");
  if (!box) return;
  box.className = type === "error" ? "flash-error" : "flash-success";
  box.textContent = message;
}

document.addEventListener("click", async (e) => {
  const btn = e.target.closest('[data-complete-ajax="true"]');
  if (!btn) return;

  e.preventDefault();

  const ok = confirm("Mark this task as completed?");
  if (!ok) return;

  const url = btn.getAttribute("data-ajax-url");
  const row = btn.closest("[data-task-row]");

  try {
    const res = await fetch(url, {
      method: "POST",
      headers: {
        "X-CSRFToken": getCookie("csrftoken"),
        "X-Requested-With": "XMLHttpRequest",
      },
    });

    const data = await res.json();
    if (!res.ok || !data.ok) throw new Error("Request failed");

    if (row) row.remove();
    const pendingList = document.getElementById("pending-list");
    if (pendingList && !pendingList.querySelector("[data-task-row]")) {
      if (!pendingList.querySelector("[data-pending-empty]")) {
        const empty = document.createElement("div");
        empty.className = "text-muted";
        empty.setAttribute("data-pending-empty", "true");
        empty.textContent = "No tasks yet.";
        pendingList.append(empty);
      }
    }

    const pendingCount = document.getElementById("pending-count");
    const completedCount = document.getElementById("completed-count");
    if (pendingCount) pendingCount.textContent = data.counts.pending;
    if (completedCount) completedCount.textContent = data.counts.completed;
    const total = data.counts.pending + data.counts.completed;
    const progress = total > 0 ? Math.round((data.counts.completed / total) * 100) : 0;

    const progressPercent = document.getElementById("progress-percent");
    const progressDetail = document.getElementById("progress-detail");
    const progressBar = document.getElementById("progress-bar");
    if (progressPercent) progressPercent.textContent = `${progress}%`;
    if (progressDetail) progressDetail.textContent = `${data.counts.completed} / ${total} done`;
    if (progressBar) {
      progressBar.style.width = `${progress}%`;
      progressBar.textContent = `${progress}%`;
      progressBar.setAttribute("aria-valuenow", String(progress));
    }

    const completedList = document.getElementById("completed-list");
    if (completedList) {
      const completedEmpty = completedList.querySelector("[data-completed-empty]");
      if (completedEmpty) completedEmpty.remove();

      const c = data.completed_task;
      const div = document.createElement("div");
      div.className = "border-bottom py-2 task-completed-item";
      div.innerHTML = `
        <div class="text-decoration-line-through"></div>
        <div class="text-muted small"></div>
      `;
      div.querySelector(".text-decoration-line-through").textContent = c.title;

      const detail = div.querySelector(".text-muted.small");
      const meta = [];
      if (c.category) meta.push(c.category);
      meta.push(`Done ${c.completed_at}`);
      detail.textContent = meta.join(" • ");

      completedList.prepend(div);
    }

    setStatus(data.message, "success");
  } catch (err) {
    setStatus("Could not mark task complete. Please try again.", "error");
  }
});

async function loadWeeklyChart() {
  const canvas = document.getElementById("weeklyChart");
  if (!canvas) return;

  try {
    const res = await fetch("/stats/weekly.json");
    const data = await res.json();
    if (!res.ok) throw new Error("Stats request failed");
    if (typeof Chart === "undefined") return;

    new Chart(canvas, {
      type: "bar",
      data: {
        labels: data.labels,
        datasets: [{ label: "Completed", data: data.values }],
      },
      options: {
        responsive: true,
        plugins: { legend: { display: false } },
        scales: {
          y: { beginAtZero: true, ticks: { precision: 0 } },
        },
      },
    });
  } catch (e) {
    console.log("Weekly chart failed:", e);
  }
}

document.addEventListener("DOMContentLoaded", loadWeeklyChart);

document.addEventListener("keydown", (e) => {
  const target = e.target;
  const isFormElement = target.matches("input, textarea, select") || target.isContentEditable;
  if (isFormElement || e.ctrlKey || e.metaKey || e.altKey) return;

  if (e.key.toLowerCase() === "t") {
    const el = document.getElementById("quickAddModal");
    if (!el || typeof bootstrap === "undefined") return;
    const modal = bootstrap.Modal.getOrCreateInstance(el);
    modal.show();
  }
});
