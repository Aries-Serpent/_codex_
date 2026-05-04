/**
 * Shared GitHub API rate-limit detector for workflow github-script steps.
 */
function isRateLimit(error) {
  const msg = [
    error?.message,
    error?.response?.data?.message,
    error?.response?.data?.error,
    error?.data?.message,
    error?.data?.error,
  ]
    .filter(Boolean)
    .join(" ")
    .toLowerCase();
  return (error?.status === 403 || error?.status === 429) && msg.includes("rate limit");
}

module.exports = { isRateLimit };
