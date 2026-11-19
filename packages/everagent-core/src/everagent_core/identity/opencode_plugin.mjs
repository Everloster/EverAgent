/** Deprecated bridge for an already configured native plugin URL.
 * The installed eacli adapter owns the hook; this file makes no model claim.
 */
import { homedir } from 'node:os';
import { join } from 'node:path';
import { pathToFileURL } from 'node:url';
const adapter = await import(pathToFileURL(join(homedir(), '.local/share/everagent/eacli-adapters/10.1.0/opencode_plugin.mjs')).href);
export default adapter.default;
