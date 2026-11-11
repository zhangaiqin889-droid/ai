export const STATUSES = ["todo", "doing", "done"];
export const PRIORITIES = ["P0", "P1", "P2"];
export function normalizeTask(value) {
  if (!value || typeof value !== "object") throw new Error("任务内容无效");
  const title = String(value.title || "").trim();
  if (!title || title.length > 120) throw new Error("标题必须在1至120字之间");
  const status = STATUSES.includes(value.status) ? value.status : "todo";
  const priority = PRIORITIES.includes(value.priority) ? value.priority : "P1";
  const id = String(value.id || "").trim();
  if (!/^[a-zA-Z0-9_-]{6,90}$/.test(id)) throw new Error("任务标识无效");
  const createdAt = Number(value.createdAt);
  if (!Number.isFinite(createdAt) || createdAt <= 0) throw new Error("创建时间无效");
  return { id, title, status, priority, createdAt };
}
export function addTask(tasks, task) {
  const item = normalizeTask(task);
  if (tasks.some(existing => existing.id === item.id)) throw new Error("任务标识重复");
  return [...tasks, item];
}
export function moveTask(tasks, id, nextStatus) {
  if (!STATUSES.includes(nextStatus)) throw new Error("未知任务状态");
  if (!tasks.some(t => t.id === id)) throw new Error("任务不存在");
  return tasks.map(t => t.id === id ? { ...t, status: nextStatus } : t);
}
export function deleteTask(tasks, id) {
  return tasks.filter(t => t.id !== id);
}
export function getStats(tasks) {
  return Object.fromEntries(STATUSES.map(status => [status, tasks.filter(t => t.status === status).length]));
}
export function exportTasks(tasks) {
  return JSON.stringify({ schema: 1, tasks: tasks.map(normalizeTask) }, null, 2);
}
export function importTasks(raw) {
  const data = JSON.parse(raw);
  if (data?.schema !== 1 || !Array.isArray(data.tasks) || data.tasks.length > 1000) throw new Error("不支持的数据格式");
  const tasks = data.tasks.map(normalizeTask);
  if (new Set(tasks.map(t => t.id)).size !== tasks.length) throw new Error("文件存在重复任务");
  return tasks;
}
