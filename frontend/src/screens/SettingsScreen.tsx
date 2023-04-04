import { SafeAreaView, ScrollView, StyleSheet, TouchableOpacity } from 'react-native';
import { Text, View } from '../components/Themed';
import { MaterialIcons } from '@expo/vector-icons';

const settings = {
  displaySettings: {
    title: 'Display Settings',
    messages: [
      "Video recording settings",
      "Language settings",
    ]
  },
  userPreferencesSettings: {
    title: 'User Settings',
    messages: [
      "Voice guidance settings",
      "Notifications settings",
    ]
  },
  privacyAndSecuritySettings: {
    title: 'Privacy and Security Settings',
    messages: [
      "Camera permissions",
    ]
  }
}

interface SettingsBlockProps {
  settings: {
    title: string;
    messages: string[];
  }
  isFinal?: Boolean,
}

const SettingsBlock = ({ settings }: SettingsBlockProps) => {
  return (
    <SafeAreaView>
      <View style={{ flex: 1, alignItems: 'center', justifyContent: 'center', marginVertical: 10 }}>
        <Text style={styles.title}>{settings.title}</Text>
        <View style={styles.separator} lightColor="#eee" darkColor="rgba(255,255,255,0.1)" />
          {settings.messages.map((message, index) => (
            <TouchableOpacity
              style={styles.listItem}
              key={index}
              onPress={() => console.log(`Setting: '${message}' pressed in '${settings.title}'`)} // make this open modal
            >
              <Text style={styles.listItemText}>{message}</Text>
              <MaterialIcons style={styles.listItemArrow} name="arrow-forward-ios" size={20} color="black" />
            </TouchableOpacity>
          ))}
        <View style={styles.separator} lightColor="#eee" darkColor="rgba(255,255,255,0.1)" />
      </View>
    </SafeAreaView>
  );
}

export default function SettingsScreen() {
  return (
    <ScrollView style={styles.container}>
      <SettingsBlock
        settings={settings.displaySettings}
      />
      <SettingsBlock
        settings={settings.userPreferencesSettings}
      />
      <SettingsBlock
        settings={settings.privacyAndSecuritySettings}
      />
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    marginHorizontal: 15,
  },
  title: {
    fontSize: 20,
    fontWeight: 'bold',
    paddingTop: 30,
  },
  separator: {
    marginVertical: 30,
    height: 1,
    width: '80%',
  },
  listItem: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    paddingVertical: 7,
    width: '80%',
  },
  listItemText: {
    textAlign: 'left',
    fontSize: 20,
  },
  listItemArrow: {
    paddingTop: 5,
  },
  buttonsContainer: {
    marginVertical: 10,
    alignItems: 'center',
  },
});
