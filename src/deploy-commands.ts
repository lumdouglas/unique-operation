/**
 * Register slash commands with Discord API.
 * Run: npm run deploy:commands
 */

import { REST, Routes } from 'discord.js';
import { config } from './config.js';
import * as orderToday from './commands/order-today.js';
import * as prepToday from './commands/prep-today.js';

const commands = [
  orderToday.data.toJSON(),
  prepToday.data.toJSON(),
];

const rest = new REST().setToken(config.discord.token);

async function deploy() {
  console.log('Deploying slash commands...');
  const result = await rest.put(
    Routes.applicationGuildCommands(config.discord.clientId, config.discord.guildId),
    { body: commands }
  ) as { length: number }[];
  console.log(`Registered ${result.length} commands.`);
}

deploy().catch(console.error);
