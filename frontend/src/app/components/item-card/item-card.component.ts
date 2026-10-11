import { Component, EventEmitter, Input, Output } from '@angular/core';

import { ChecklistItem } from '../../models/optimizer';

@Component({
  selector: 'app-item-card',
  templateUrl: './item-card.component.html',
  styleUrl: './item-card.component.css',
})
export class ItemCardComponent {
  @Input({ required: true }) item!: ChecklistItem;
  @Input() checked = false;
  @Output() toggled = new EventEmitter<void>();

  get stashYields() {
    return this.item.yields.filter((row) => row.context === 'in_stash');
  }

  get raidYields() {
    return this.item.yields.filter((row) => row.context === 'in_raid');
  }
}
