/**
 * /order-today — Modal: recipe select + servings + notes
 */

import {
  SlashCommandBuilder,
  ModalBuilder,
  TextInputBuilder,
  TextInputStyle,
  ActionRowBuilder,
  type ChatInputCommandInteraction,
  type ModalSubmitInteraction,
} from 'discord.js';
import { getRecipes, createOrder } from '../lib/order-service.js';

export const CUSTOM_ID = 'order_today_modal';

export const data = new SlashCommandBuilder()
  .setName('order-today')
  .setDescription('Add a daily order (recipe + servings + notes)');

export async function execute(interaction: ChatInputCommandInteraction) {
  const recipes = await getRecipes();
  if (!recipes.length) {
    await interaction.reply({
      content: 'No recipes in the database. Add recipes first.',
      ephemeral: true,
    });
    return;
  }

  const modal = new ModalBuilder()
    .setCustomId(CUSTOM_ID)
    .setTitle('Add Daily Order');

  const recipeInput = new TextInputBuilder()
    .setCustomId('recipe')
    .setLabel('Recipe name')
    .setStyle(TextInputStyle.Short)
    .setPlaceholder(recipes[0]?.name ?? 'e.g. Spicy Tuna Roll')
    .setRequired(true);

  const servingsInput = new TextInputBuilder()
    .setCustomId('servings')
    .setLabel('Servings')
    .setStyle(TextInputStyle.Short)
    .setPlaceholder('e.g. 50')
    .setRequired(true);

  const notesInput = new TextInputBuilder()
    .setCustomId('notes')
    .setLabel('Notes (optional)')
    .setStyle(TextInputStyle.Paragraph)
    .setPlaceholder('Special instructions, delivery time, etc.')
    .setRequired(false);

  modal.addComponents(
    new ActionRowBuilder<TextInputBuilder>().addComponents(recipeInput),
    new ActionRowBuilder<TextInputBuilder>().addComponents(servingsInput),
    new ActionRowBuilder<TextInputBuilder>().addComponents(notesInput)
  );

  await interaction.showModal(modal);
}

/** Handle modal submit from order-today */
export async function handleModalSubmit(
  interaction: ModalSubmitInteraction
) {
  const recipeInput = interaction.fields.getTextInputValue('recipe').trim();
  const servingsStr = interaction.fields.getTextInputValue('servings').trim();
  const notes = interaction.fields.getTextInputValue('notes').trim() || null;

  const servings = parseFloat(servingsStr);
  if (isNaN(servings) || servings <= 0) {
    await interaction.reply({
      content: 'Invalid servings. Please enter a positive number.',
      ephemeral: true,
    });
    return;
  }

  const recipes = await getRecipes();
  const match = recipes.find(
    (r) =>
      r.id === recipeInput ||
      r.name.toLowerCase() === recipeInput.toLowerCase()
  );
  const recipeId = match?.id ?? null;

  if (!recipeId) {
    await interaction.reply({
      content: `Recipe not found: "${recipeInput}". Check spelling or use an existing recipe name.`,
      ephemeral: true,
    });
    return;
  }

  await createOrder({ recipe_id: recipeId, servings, notes });
  await interaction.reply({
    content: `✅ Order added: **${servings}** servings. Use \`/prep-today\` to post prep lists.`,
    ephemeral: true,
  });
}
