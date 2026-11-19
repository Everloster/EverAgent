/** Deprecated compatibility bridge for an already configured file:// URL.
 * Identity implementation is exported by installed eacli, never this checkout.
 * Keep until the owning profile is rebound in an idle maintenance window.
 */
import { homedir } from 'node:os';
import { join } from 'node:path';
import { pathToFileURL } from 'node:url';
const adapter = await import(pathToFileURL(join(homedir(), '.local/share/everagent/eacli-adapters/10.1.0/dsh_plugin.mjs')).href);
export const name = adapter.name;
export const inject = adapter.inject;
export const apply = adapter.apply;
