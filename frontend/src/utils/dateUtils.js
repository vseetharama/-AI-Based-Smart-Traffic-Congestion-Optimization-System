export function formatTimestamp(timestamp) {
  if (!timestamp) return "Not available";
  const date = new Date(timestamp);
  if (Number.isNaN(date.getTime())) return "Not available";

  const day = String(date.getDate()).padStart(2, "0");
  const month = String(date.getMonth() + 1).padStart(2, "0");
  const year = date.getFullYear();

  let hours = date.getHours();
  const minutes = String(date.getMinutes()).padStart(2, "0");
  const seconds = String(date.getSeconds()).padStart(2, "0");
  const period = hours >= 12 ? "PM" : "AM";
  hours = hours % 12 || 12;
  const hourString = String(hours).padStart(2, "0");

  return `${day}-${month}-${year} ${hourString}:${minutes}:${seconds} ${period}`;
}

export function formatTime(timestamp) {
  if (!timestamp) return "Not available";
  const date = new Date(timestamp);
  if (Number.isNaN(date.getTime())) return "Not available";

  let hours = date.getHours();
  const minutes = String(date.getMinutes()).padStart(2, "0");
  const seconds = String(date.getSeconds()).padStart(2, "0");
  const period = hours >= 12 ? "PM" : "AM";
  hours = hours % 12 || 12;
  const hourString = String(hours).padStart(2, "0");

  return `${hourString}:${minutes}:${seconds} ${period}`;
}
