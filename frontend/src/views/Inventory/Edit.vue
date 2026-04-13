<template>
  <section>
    <h1 class="text-3xl font-bold mb-6">Edit Equipment</h1>

    <p v-if="error" class="text-red-600 mb-4">{{ error }}</p>

    <form @submit.prevent="submitForm" class="bg-white rounded-lg shadow p-6 max-w-md">
      <div class="mb-4">
        <fwb-input
          v-model="form.equipmentName"
          label="Equipment Name"
          placeholder="enter equipment name"
          size="md"
          required
        />
      </div>

      <div class="mb-4">
        <fwb-input
          v-model.number="form.price"
          label="Price"
          type="number"
          :step="0.01"
          :min="0"
          size="md"
          required
        />
      </div>

      <div class="mb-4">
        <fwb-select
          v-model="form.condition"
          :options="conditions"
          label="Condition"
          size="md"
        />
      </div>

      <div class="mb-4">
        <fwb-input
          v-model="form.description"
          label="Description"
          placeholder="enter equipment description"
          size="md"
        />
      </div>

      <div class="mb-4" v-if="displayFileUploadButton == true">
        <label class="block mb-2 text-sm font-medium text-black-700">
          Upload Equipment Picture (.jpeg / .jpg / .png / .webp)
        </label>

        <fwb-button
          @click="onClickDisplayFileUploadBox"
          color="blue"
          size="md"
          square
        >
          <DocumentArrowUpIcon class="w-5 h-5" />
        </fwb-button>
      </div>

      <div class="mb-4" v-if="displayFileUploadBox == true">
        <fwb-file-input
          v-model="equipmentPhoto"
          accept="image/jpeg,image/png,image/webp"
          label="Upload Equipment Picture (.jpeg / .jpg / .png / .webp)"
          @change="handleFileChange"
          dropzone
        />
      </div>

      <div class="mb-4 flex gap-2" v-if="displayFileUploadBox == true">
        <fwb-button
          :disabled="canUploadPhoto == false"
          @click="onClickUploadFile"
          size="md"
        >
          Upload
        </fwb-button>
        <fwb-button
          @click="onClickDisplayFileUploadButton"
          color="red"
          size="md"
        >
          Cancel
        </fwb-button>
      </div>

      <div class="mb-4" v-if="displayFileUploadSpinner == true">
        <label class="block mb-2 text-sm font-medium text-black-700">
          Upload Equipment Picture (.jpeg / .jpg / .png / .webp)
        </label>

        <fwb-spinner size="10" />
      </div>

      <div class="mb-4" v-if="displayFileUploadPhoto == true">
        <label class="block mb-2 text-sm font-medium text-black-700">
          Upload Equipment Picture (.jpeg / .jpg / .png / .webp)
        </label>

        <fwb-img 
          alt="Equipment Picture"
          img-class="w-full h-48 object-cover rounded-lg border-2 border-black"
          size="max-w-md"
          :src="`${BACKEND_URL}/${form.picture}`"
        />
      </div>

      <div class="mb-4 flex gap-2" v-if="displayFileUploadPhoto == true">
        <fwb-button
          @click="onClickReuploadFile"
          size="md"
        >
          Re-upload
        </fwb-button>
        <fwb-button
          @click="onClickCancelUploadedFile"
          color="red"
          size="md"
        >
          Cancel
        </fwb-button>
      </div>

      <button
        type="submit"
        :disabled="loading"
        class="w-full px-4 py-2 bg-blue-600 text-white font-medium rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
      >
        {{ loading ? 'Saving...' : 'Save Changes' }}
      </button>
    </form>
  </section>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { FwbInput, FwbSelect, FwbButton, FwbFileInput, FwbImg, FwbSpinner } from 'flowbite-vue'
import { DocumentArrowUpIcon } from '@heroicons/vue/24/solid'
import { useAuthStore } from '../../stores/auth'
import equipmentService from '../../services/equipmentService'

const conditions = [
  { value: 'Mint', name: '🔵 Mint' },
  { value: 'Above Average', name: '🟢 Above Average' },
  { value: 'Average', name: '🟡 Average' },
  { value: 'Below Average', name: '🔴 Below Average' }
]

const BACKEND_URL = import.meta.env.VITE_BACKEND_URL

const MAX_FILE_SIZE = 2 * 1024 * 1024

const auth = useAuthStore()
const router = useRouter()
const route = useRoute()
const loading = ref(false)
const error = ref('')
const OWNER_ID = computed(() => auth.user?.id)

const displayFileUploadButton = ref(true)
const displayFileUploadBox = ref(false)
const displayFileUploadSpinner = ref(false)
const displayFileUploadPhoto = ref(false)
const canUploadPhoto = ref(false)
const equipmentPhoto = ref(null)

const form = ref({
  equipmentName: '',
  price: 0,
  condition: '',
  description: '',
  picture: '',
})

onMounted(async () => {
  const id = route.params.id
  if (id) {
    try {
      // Getting the form data
      const equipment = await equipmentService.getEquipmentById(id)
      form.value.equipmentName = equipment.name
      form.value.price = equipment.price
      form.value.description = equipment.description || ''
      form.value.picture = equipment.picture || ''
      form.value.condition = equipment.condition

      // If the equipment already has a picture, then display it.
      if (form.value.picture !== '') {
        displayFileUploadButton.value = false
        displayFileUploadBox.value = false
        displayFileUploadPhoto.value = true
        displayFileUploadSpinner.value = false
        canUploadPhoto.value = false
      }
    } catch (e) {
      error.value = 'Unable to load equipment for editing'
      console.error(e)
    }
  } else {
    error.value = 'Missing equipment id'
  }
})

const submitForm = async () => {
  loading.value = true
  error.value = ''
  try {
    const id = route.params.id

    if (!id) {
      throw new Error('Missing equipment id')
    }

    await equipmentService.updateEquipment(
      id,
      form.value.equipmentName,
      OWNER_ID.value,
      form.value.price,
      form.value.description,
      form.value.picture,
      form.value.condition
    )

    router.push({ name: 'inventory' })
  } catch (err) {
    error.value = err.message || 'Failed to update equipment'
    console.error('Error updating equipment:', err)
  } finally {
    loading.value = false
  }
}

function onClickDisplayFileUploadBox() {
  displayFileUploadButton.value = false
  displayFileUploadBox.value = true
  displayFileUploadSpinner.value = false
  displayFileUploadPhoto.value = false
  canUploadPhoto.value = false
}

function onClickDisplayFileUploadButton() {
  displayFileUploadButton.value = true
  displayFileUploadBox.value = false
  displayFileUploadSpinner.value = false
  displayFileUploadPhoto.value = false
  canUploadPhoto.value = false

  // Setting the equipment picture reference back to null
  equipmentPhoto.value = null

  // Setting the equipment picture dirctory back to an empty string
  form.value.picture = ''
}

function handleFileChange(event) {
  // Getting the file
  const file = event.target.files[0]

  if (!file) {
    return
  }

  // Validating that the file is the correct file type
  const allowedTypes = [
    'image/jpeg',
    'image/png',
    'image/webp'
  ]

  if (allowedTypes.includes(file.type) == false) {
    canUploadPhoto.value = false
    equipmentPhoto.value = null
    alert('Invalid file type. Please upload JPG, PNG, or WebP.')
    return
  }

  // Validating that the file is not too large
  if (file.size > MAX_FILE_SIZE) {
    canUploadPhoto.value = false
    equipmentPhoto.value = null
    alert("The inputted picture file is too large. The maximum file size is 2 MB.")
    return
  }

  // Allowing the user to upload the file
  canUploadPhoto.value = true
}

async function onClickUploadFile() {
  displayFileUploadButton.value = false
  displayFileUploadBox.value = false
  displayFileUploadPhoto.value = false
  displayFileUploadSpinner.value = true
  canUploadPhoto.value = false

  // Sending the picture to be saved in the backend
  const file = equipmentPhoto.value
  let result = await equipmentService.uploadEquipmentPicture(file)

  // Checking if the picture was successfully stored in the backend
  if (result.success == false) {
    alert("Picture file did not upload properly. Please try again.")

    // Resetting to the file upload box
    onClickDisplayFileUploadBox()

    // Setting the equipment picture reference back to null
    equipmentPhoto.value = null

    // Setting the equipment picture dirctory back to an empty string
    form.value.picture = ''

    return
  }

  // Storing the picture filepath in the form object for the equipment
  form.value.picture = result.filename

  // Displaying the picture to the user
  displayFileUploadSpinner.value = false
  displayFileUploadPhoto.value = true
}

async function onClickCancelUploadedFile() {
  displayFileUploadButton.value = true
  displayFileUploadBox.value = false
  displayFileUploadPhoto.value = false
  displayFileUploadSpinner.value = false
  canUploadPhoto.value = false

  // Setting the equipment picture reference back to null
  equipmentPhoto.value = null

  // Delete the photo from the backend
  let result = await equipmentService.deleteUploadedEquipmentPicture(form.value.picture)
  
  // Setting the equipment picture dirctory back to an empty string
  form.value.picture = ''
}

async function onClickReuploadFile() {
  displayFileUploadButton.value = false
  displayFileUploadBox.value = true
  displayFileUploadPhoto.value = false
  displayFileUploadSpinner.value = false
  canUploadPhoto.value = false

  // Setting the equipment picture reference back to null
  equipmentPhoto.value = null

  // Delete the photo from the backend
  let result = await equipmentService.deleteUploadedEquipmentPicture(form.value.picture)

  // Setting the equipment picture dirctory back to an empty string
  form.value.picture = ''
}

</script>
