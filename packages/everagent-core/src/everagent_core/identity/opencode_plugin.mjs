/** OpenCode 1.18.32 official shell.env hook. Only binds the active tool;
 * Go reads its scalar SQLite metadata. No model claim, file, key or body.
 */
export default async () => ({
  'shell.env': async (input, output) => {
    // Clear inherited values when a shell has no native tool/session binding.
    output.env.OPENCODE_SESSION_ID = input.sessionID ?? '';
    output.env.OPENCODE_CALL_ID = input.callID ?? '';
    output.env.OPENCODE_RUNTIME_PID = String(process.pid);
  },
});
