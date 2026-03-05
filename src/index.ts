/**
 * Sushi Logistics Discord Bot
 * Phase 1: /order-today, /prep-today → 3 embeds
 */

import {
  Client,
  GatewayIntentBits,
  Events,
  type ChatInputCommandInteraction,
  type ModalSubmitInteraction,
} from 'discord.js';
import { config } from './config.js';
import * as orderToday from './commands/order-today.js';

const commands = new Map<
  string,
  {
    data: { name: string; toJSON: () => unknown };
    execute: (i: ChatInputCommandInteraction) => Promise<void>;
  }
>();

async function registerCommands() {
  const orderTodayCmd = await import('./commands/order-today.js');
  const prepTodayCmd = await import('./commands/prep-today.js');
  commands.set(orderTodayCmd.data.name, orderTodayCmd);
  commands.set(prepTodayCmd.data.name, prepTodayCmd);
}

const client = new Client({
  intents: [GatewayIntentBits.Guilds],
});

client.once(Events.ClientReady, async (c) => {
  console.log(`Logged in as ${c.user.tag}`);
  await registerCommands();
});

client.on(Events.InteractionCreate, async (interaction) => {
  if (interaction.isChatInputCommand()) {
    const cmd = commands.get(interaction.commandName);
    if (cmd) {
      try {
        await cmd.execute(interaction);
      } catch (err) {
        console.error(err);
        const reply = { content: 'Something went wrong.', ephemeral: true };
        if (interaction.replied || interaction.deferred) {
          await interaction.followUp(reply).catch(() => {});
        } else {
          await interaction.reply(reply).catch(() => {});
        }
      }
    }
  } else if (interaction.isModalSubmit()) {
    if (interaction.customId === orderToday.CUSTOM_ID) {
      try {
        await orderToday.handleModalSubmit(interaction as ModalSubmitInteraction);
      } catch (err) {
        console.error(err);
        await interaction
          .reply({ content: 'Failed to save order.', ephemeral: true })
          .catch(() => {});
      }
    }
  }
});

client.login(config.discord.token);
