import os
from flask import Flask, render_template, request, redirect, url_for, flash
from garden.storage import Storage
from garden.exceptions import GardenLogicError

app = Flask(__name__)
app.secret_key = os.urandom(24)
storage = Storage()

@app.route('/')
def index():
    plot = storage.load()
    return render_template('index.html', plot=plot)

@app.route('/action', methods=['POST'])
def action():
    plot = storage.load()
    action_type = request.form.get('action')

    try:
        if action_type == 'plant':
            species = request.form.get('species')
            if species:
                plot.plant_seed(species)
        elif action_type == 'water':
            plot.water_garden()
        elif action_type == 'refill_water':
            plot.refill_water()
        elif action_type == 'fertilize':
            plot.fertilize_soil()
        elif action_type == 'weed':
            plot.weed_plants()
        elif action_type == 'grow':
            msgs = plot.process_growth()
            for m in msgs:
                flash(m, 'info')
        elif action_type == 'build_zone':
            plot.develop_recreation_zone()
        elif action_type == 'decorate':
            item = request.form.get('item')
            if item:
                plot.decorate_zone(item)
        elif action_type == 'repair':
            idx = int(request.form.get('tool_index', -1))
            if 0 <= idx < len(plot.tools):
                plot.maintain_tool(idx)
    except GardenLogicError as e:
        flash(str(e), 'error')
    except ValueError:
        flash("Ошибка формата ввода.", 'error')

    storage.save(plot)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)