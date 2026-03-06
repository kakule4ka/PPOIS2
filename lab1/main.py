import sys
from garden.storage import Storage
from garden.exceptions import GardenLogicError

def print_status(plot):
    moisture = "ДА" if plot.soil.is_hydrated else "НЕТ"
    fertility = "ДА" if plot.soil.is_fertilized else "НЕТ"
    water = f"{plot.watering_system.current_water}/{plot.watering_system.max_capacity}"
    zone = f"{plot.recreation_zone.build_progress}%"
    decor = ", ".join(plot.recreation_zone.decorations) if plot.recreation_zone.decorations else "пусто"

    print("\n" + "=" * 54)
    print(" СОСТОЯНИЕ УЧАСТКА")
    print("-" * 54)
    print(f" ПОЧВА:         Влага: {moisture:<5} | Удобрения: {fertility}")
    print(f" ВОДА В БАКЕ:   {water}")
    print(f" ЗОНА ОТДЫХА:   Готовность {zone:<4} | Декор: {decor}")
    
    print("\n РАСТЕНИЯ:")
    if not plot.plants:
        print(" (нет посадок)")
    for i, p in enumerate(plot.plants):
        print(f" [{i}] {p.species:<15} -> {p.state.value}")
            
    print("\n ИНСТРУМЕНТЫ:")
    for i, t in enumerate(plot.tools):
        print(f" [{i}] {t.name:<15} -> Прочность: {t.durability}%")
    print("=" * 54)

def print_menu():
    print("\n1. Посадить семечко      2. Полить участок")
    print("3. Наполнить бак водой   4. Удобрить почву")
    print("5. Прополоть сорняки     6. Цикл роста")
    print("7. Строить зону отдыха   8. Добавить декор")
    print("9. Починить инструмент   0. Сохранить и выйти")
    print("-" * 54)

def main():
    storage = Storage()
    plot = storage.load()

    while True:
        print_status(plot)
        print_menu()
        
        try:
            choice = input("Действие > ")
            
            if choice == "1":
                species = input("Растение: ")
                plot.plant_seed(species)
            elif choice == "2":
                required_water = 10 if not plot.plants else len(plot.plants) * 10
                if plot.watering_system.current_water < required_water:
                    print(f"\n[ВНИМАНИЕ] Нужно {required_water} ед. воды, а в баке {plot.watering_system.current_water}.")
                    ans = input("Наполнить бак и полить участок? (y/n): ").strip().lower()
                    if ans == 'y':
                        plot.refill_water()
                        plot.water_garden()
                    else:
                        print("\nПолив отменен.")
                else:
                    plot.water_garden()
            elif choice == "3":
                plot.refill_water()
            elif choice == "4":
                plot.fertilize_soil()
            elif choice == "5":
                plot.weed_plants()
            elif choice == "6":
                msgs = plot.process_growth()
                print("\n--- Отчет о росте ---")
                for m in msgs:
                    print(f" {m}")
            elif choice == "7":
                plot.develop_recreation_zone()
            elif choice == "8":
                item = input("Декор: ")
                plot.decorate_zone(item)
            elif choice == "9":
                idx = int(input("Индекс инструмента (0-Лопата, 1-Грабли, 2-Молоток): "))
                plot.maintain_tool(idx)
            elif choice == "0":
                storage.save(plot)
                sys.exit()
        except GardenLogicError as e:
            print(f"\n[ОТКАЗ] {e}")
        except ValueError:
            print("\n[ОШИБКА ВВОДА] Неверный формат.")
        except IndexError:
            print("\n[ОШИБКА] Индекс вне диапазона.")
        except KeyboardInterrupt:
            print("\n[ВНИМАНИЕ] Пожалуйста, используйте пункт 0 для безопасного выхода.")

if __name__ == "__main__":
    main()