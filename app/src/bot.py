from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardRemove, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext, ConversationHandler, CallbackQueryHandler
from peewee import *

# Connect to your database
db = PostgresqlDatabase('testik6', user='bogdanafter', password='bogdanafter', host='192.168.1.206', port=5432)

# Define conversation states
CITY, ZONE, CABINET = range(3)

class BaseModel(Model):
    class Meta:
        database = db

# Models for city, zone, cabinet, and slots
class ss_main_city(BaseModel):
    city_name = CharField(max_length=255, unique=True, null=False)
    country = CharField(max_length=255, null=False)

class ss_main_zone(BaseModel):
    zone_name = CharField(max_length=255, unique=True, null=False)
    city = ForeignKeyField(ss_main_city, backref='zones', null=False, on_delete='CASCADE')

class Ss_main_cabinet(BaseModel):
    city = ForeignKeyField(ss_main_city, backref='cabinets', null=False, on_delete='CASCADE')
    shkaf_id = CharField(null=False, unique=True, max_length=255)
    zone = ForeignKeyField(ss_main_zone, backref='cabinets', null=False, on_delete='CASCADE')

class ss_main_cell(BaseModel):
    cabinet_id_id = ForeignKeyField(Ss_main_cabinet, field=Ss_main_cabinet.shkaf_id, related_name='shkaf_id', on_delete='CASCADE')
    vir_sn_eid = TextField(null=True, verbose_name='VIR_SN_EID')
    cap_percent = CharField(null=True, column_name='cap_percent')
    status = CharField(null=True, verbose_name='status')
    is_error = BooleanField(null=True, verbose_name='is_error', default=False)
    message = CharField(null=True, verbose_name='MESSAGE')

# Start the conversation
async def start(update: Update, context: CallbackContext):
    cities = ss_main_city.select()
    city_list = [city.city_name for city in cities]

    # Reply with available cities
    await update.message.reply_text(
        "Please select a city:",
        reply_markup=ReplyKeyboardMarkup([city_list], one_time_keyboard=True)
    )
    return CITY

# Handle city selection
async def city_selection(update: Update, context: CallbackContext):
    selected_city = update.message.text
    context.user_data['city'] = selected_city

    # Get available zones for the selected city
    zones = ss_main_zone.select().where(ss_main_zone.city == selected_city)
    zone_list = [zone.zone_name for zone in zones]

    await update.message.reply_text(
        f"You selected {selected_city}. Now choose a zone:",
        reply_markup=ReplyKeyboardMarkup([zone_list], one_time_keyboard=True)
    )
    return ZONE

# Handle zone selection
async def zone_selection(update: Update, context: CallbackContext):
    selected_zone = update.message.text
    context.user_data['zone'] = selected_zone

    # Get cabinets in the selected city and zone
    selected_city = context.user_data['city']
    cabinets = Ss_main_cabinet.select().where(
        (Ss_main_cabinet.city == selected_city) & (Ss_main_cabinet.zone == selected_zone)
    )
    cabinet_list = [cabinet.shkaf_id for cabinet in cabinets]

    await update.message.reply_text(
        f"Available cabinets in {selected_zone}:\n" + "\n".join(cabinet_list)
    )
    return CABINET

# Handle cabinet selection and show slot info
async def cabinet_selection(update: Update, context: CallbackContext):
    selected_cabinet = update.message.text
    context.user_data['cabinet'] = selected_cabinet

    # Get slots in the selected cabinet
    slots = ss_main_cell.select().where(ss_main_cell.cabinet_id_id == selected_cabinet).order_by(ss_main_cell.vir_sn_eid)

    # Prepare formatted slot information
    header = "Slot Information for Cabinet {}\n".format(selected_cabinet)
    header += "{:<15} {:<10} {:<10} {:<10} {:<10}\n".format("Slot ID", "%", "STATUS", "ERROR", "MESSAGE")
    header += "-" * 70 + "\n"  # Adjusted the line length for better alignment

    slot_info = ""
    for slot in slots:
        slot_info += "{:<15} {:<10} {:<10} {:<10} {:<10}\n".format(
            slot.vir_sn_eid,
            slot.cap_percent if slot.cap_percent else '-',
            slot.status,
            str(slot.is_error),
            slot.message if slot.message else '-'
        )

    # Combine header and slot information
    message_text = header + slot_info if slot_info else "No slots available for this cabinet."

    # Add the "Update" button
    keyboard = [[InlineKeyboardButton("Update", callback_data=f"update_{selected_cabinet}")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(message_text, reply_markup=reply_markup)

# Handle the "Update" button callback to refresh slot information
async def update_slot_info(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()

    # Get cabinet ID from callback data
    cabinet_id = query.data.split("_")[1]

    # Get updated slots in the cabinet
    slots = ss_main_cell.select().where(ss_main_cell.cabinet_id_id == cabinet_id).order_by(ss_main_cell.vir_sn_eid)

    # Prepare updated slot information
    header = "Updated Slot Information for Cabinet {}\n".format(cabinet_id)
    header += "{:<15} {:<10} {:<10} {:<10} {:<10}\n".format("VIR_SN_EID", "CAP_PERCENT", "STATUS", "ERROR", "MESSAGE")
    header += "-" * 70 + "\n"

    slot_info = ""
    for slot in slots:
        slot_info += "{:<15} {:<10} {:<10} {:<10} {:<10}\n".format(
            slot.vir_sn_eid,
            slot.cap_percent if slot.cap_percent else '-',
            slot.status,
            str(slot.is_error),
            slot.message if slot.message else '-'
        )

    # Combine header and updated slot information
    message_text = header + slot_info if slot_info else "No slots available for this cabinet."

    # Update the original message with the refreshed data
    await query.edit_message_text(text=message_text, reply_markup=InlineKeyboardMarkup(
        [[InlineKeyboardButton("Update", callback_data=f"update_{cabinet_id}")]]))


# Cancel the conversation
async def cancel(update: Update, context: CallbackContext):
    await update.message.reply_text('Operation cancelled.', reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END

# Initialize the bot
application = Application.builder().token('5390647299:AAG1pA7KxfyX01CIUShsnl-yfaUEHACBTjM').build()

# Conversation handler for selecting city, zone, and cabinet
conv_handler = ConversationHandler(
    entry_points=[CommandHandler('start', start)],
    states={
        CITY: [MessageHandler(filters.TEXT & ~filters.COMMAND, city_selection)],
        ZONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, zone_selection)],
        CABINET: [MessageHandler(filters.TEXT & ~filters.COMMAND, cabinet_selection)]
    },
    fallbacks=[CommandHandler('cancel', cancel)]
)

# Add handlers to the application
application.add_handler(conv_handler)
application.add_handler(CallbackQueryHandler(update_slot_info, pattern=r"update_\d+"))

# Start the bot
if __name__ == '__main__':
    application.run_polling()
