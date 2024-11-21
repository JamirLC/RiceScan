import { createVuetify } from 'vuetify';
import 'vuetify/styles';

const vuetify = createVuetify({
    icons: {
      defaultSet: 'mdi',  // This should be 'mdi' if you're using Material Design Icons
    }
  });

export default vuetify;
