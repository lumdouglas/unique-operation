/**
 * Environment configuration. All secrets from env vars.
 */

function requireEnv(name: string): string {
  const val = process.env[name];
  if (!val) throw new Error(`Missing required env: ${name}`);
  return val;
}

export const config = {
  discord: {
    token: requireEnv('DISCORD_TOKEN'),
    clientId: requireEnv('DISCORD_CLIENT_ID'),
    guildId: requireEnv('DISCORD_GUILD_ID'),
    chefViewChannelId: requireEnv('DISCORD_CHEF_VIEW_CHANNEL_ID'),
    prepViewChannelId: requireEnv('DISCORD_PREP_VIEW_CHANNEL_ID'),
    packViewChannelId: requireEnv('DISCORD_PACK_VIEW_CHANNEL_ID'),
  },
  supabase: {
    url: requireEnv('SUPABASE_URL'),
    serviceRoleKey: requireEnv('SUPABASE_SERVICE_ROLE_KEY'),
  },
} as const;
